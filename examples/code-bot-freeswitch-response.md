## Question
Implement a Freeswitch module exposing the command stream_while_ringing API command. We have two channels aleg and bleg. The command stream_while_ringing takes two arguments: aleg channel and bleg channel. Ability to stream the audio from aleg channel to bleg channel if aleg channel is in state ringing or early media. Stop streaming if aleg or bleg channels hangs up or aleg channel state changes to answered. The command stream_while_ringing should be executed in background. To start streaming the command stream_while_ringing should be set with two arguments: aleg channel uuid and bleg channel uuid. To stop manually the audio streaming, the command stream_while_ringing should take two arguments: aleg channel uuid and stop. The two channels aleg and bleg are not bridged, use switch_core_media_bug to stream the audio out from aleg and stream in into bleg.

## Answer
```c
#include <switch.h>

SWITCH_MODULE_LOAD_FUNCTION(mod_stream_while_ringing_load);
SWITCH_MODULE_DEFINITION(mod_stream_while_ringing, mod_stream_while_ringing_load, NULL, NULL);


#define STREAM_WHILE_RINGING_SYNTAX "<aleg_uuid> <bleg_uuid>"
#define STREAM_WHILE_RINGING_STOP_SYNTAX "<aleg_uuid> stop"


typedef struct {
    switch_memory_pool_t *pool;
    switch_thread_t *thread;
    switch_channel_t *channel;
    switch_channel_t *peer_channel;
    const char *aleg_uuid;
    const char *bleg_uuid;
    int done;
} stream_while_ringing_thread_data_t;


static void *SWITCH_THREAD_FUNC stream_while_ringing_thread_run(switch_thread_t *thread, void *obj)
{
    stream_while_ringing_thread_data_t *data = obj;

    switch_core_session_t *aleg_session = switch_core_session_locate(data->aleg_uuid);
    switch_channel_t *aleg_channel = switch_core_session_get_channel(aleg_session);

    switch_core_session_t *bleg_session = switch_core_session_locate(data->bleg_uuid);
    switch_channel_t *bleg_channel = switch_core_session_get_channel(bleg_session);

    switch_media_bug_t *bug;
    switch_status_t status;
    switch_state_handler_table_t *bleg_state_handlers = NULL;

    if (!aleg_channel || ! ble_channel) {
        goto done;
    }

    if ((status = switch_core_media_bug_add(aleg_channel, SWITCH_TRUE, "mod_stream_while_ringing", NULL, NULL, NULL, NULL, SMDR_ANY, &bug)) != SWITCH_STATUS_SUCCESS) {
        goto done;
    }

    switch_core_media_bug_set(bug, SWITCH_TRUE, SWITCH_MMEDIA_TYPE_AUDIO, SWITCH_FALSE, SWITCH_TRUE, SWITCH_TRUE, SWITCH_DEFAULT_RECORD_READ_SIZE);

    if ((status = switch_core_media_bug_add(bleg_channel, SWITCH_TRUE, "mod_stream_while_ringing", NULL, NULL, NULL, NULL, SMDR_ANY, &bug)) != SWITCH_STATUS_SUCCESS) {
        goto done;
    }

    switch_core_media_bug_set(bug, SWITCH_FALSE, SWITCH_MMEDIA_TYPE_AUDIO, SWITCH_TRUE, SWITCH_TRUE, SWITCH_TRUE, SWITCH_DEFAULT_RECORD_READ_SIZE);

    while(!data->done) {
        if(switch_channel_test_flag(aleg_channel, CF_ANSWERED)) {
            break;
        }

        if(switch_channel_test_flag(aleg_channel, CF_PROGRESS) || switch_channel_test_flag(aleg_channel, CF_RINGING)) {
            if (!bleg_state_handlers) {
                bleg_state_handlers = switch_channel_get_state_handlers(bleg_channel);
                switch_channel_set_state_handler(aleg_channel, bleg_state_handlers);
            }
        } else {
            if (bleg_state_handlers) {
                switch_channel_set_state_handler(aleg_channel, NULL);
                bleg_state_handlers = NULL;
            }
        }

        switch_yield(50000);
    }

done:
    if (bleg_state_handlers) {
        switch_channel_set_state_handler(aleg_channel, NULL);
    }

    if (bleg_session) {
        switch_core_session_rwunlock(bleg_session);
    }

    if (aleg_session) {
        switch_core_session_rwunlock(aleg_session);
    }

    return NULL;
}


static switch_status_t stream_while_ringing(session_t *session, char *cmd, char *args, stream_handle_t *stream)
{
    stream_while_ringing_thread_data_t *data = NULL;
    switch_status_t status = SWITCH_STATUS_SUCCESS;
    const char *delim = " ";
    char *arg1, *arg2;
    int argc;

    if (!args) {
        goto err;
    }

    argc = switch_separate_string(args, delim, NULL, 0);
    if (argc == 2) {
        arg1 = switch_separate_string(args, delim, 0);
        arg2 = switch_separate_string(args, delim, 1);

        data = switch_core_alloc(session->pool, sizeof(stream_while_ringing_thread_data_t));
        memset(data, 0, sizeof(*data));
        data->pool = session->pool;
        data->aleg_uuid = arg1;
        data->bleg_uuid = arg2;
        data->done = 0;

        switch_thread_create(&data->thread, NULL, stream_while_ringing_thread_run, data, data->pool);

        stream->write_function(stream, "+OK\n");
    } else if (argc == 2 && !strcasecmp(arg2, "stop")) {
        arg1 = switch_separate_string(args, delim, 0);

        if (!data || strcasecmp(arg1, data->aleg_uuid)) {
            goto err;
        }

        if (!data->done) {
            data->done = 1;
            switch_thread_join(data->thread, NULL);
        }

        switch_core_session_t *aleg_session = switch_core_session_locate(data->aleg_uuid);
        switch_channel_t *aleg_channel = switch_core_session_get_channel(aleg_session);

        switch_core_session_t *bleg_session = switch_core_session_locate(data->bleg_uuid);
        switch_channel_t *bleg_channel = switch_core_session_get_channel(bleg_session);

        if (aleg_channel) {
            switch_core_media_bug_remove(aleg_channel, "mod_stream_while_ringing");
        }

        if (bleg_channel) {
            switch_core_media_bug_remove(bleg_channel, "mod_stream_while_ringing");
        }

        if (aleg_session) {
            switch_core_session_rwunlock(aleg_session);
        }

        if (bleg_session) {
            switch_core_session_rwunlock(bleg_session);
        }

        switch_core_free(data);

        stream->write_function(stream, "+OK\n");
    } else {
        goto err;
    }

    return status;

err:
    stream->write_function(stream, "-ERR Usage: stream_while_ringing <aleg_uuid> <bleg_uuid> | stream_while_ringing <aleg_uuid> stop\n");
    return status;
}


SWITCH_MODULE_LOAD_FUNCTION(mod_stream_while_ringing_load)
{
    switch_api_interface_t *api_interface;

    memset(&globals, 0, sizeof(globals));
    globals.pool = pool;

    *module_interface = switch_loadable_module_create_module_interface(pool, modname);

    /* add api commands */
    SWITCH_ADD_API(api_interface, "stream_while_ringing", "Stream audio while aleg is ringing", stream_while_ringing, STREAM_WHILE_RINGING_SYNTAX, SAF_NONE);
    SWITCH_ADD_API(api_interface, "stream_while_ringing_stop", "Stop streaming audio during aleg ringing", stream_while_ringing, STREAM_WHILE_RINGING_STOP_SYNTAX, SAF_NONE);

    return SWITCH_STATUS_SUCCESS;
}
```

LANGUAGE: C



## References
https://github.com/signalwire/freeswitch/blob/master/src/switch_ivr.c
https://github.com/signalwire/freeswitch/blob/master/src/mod/endpoints/mod_sofia/sofia.c
https://github.com/signalwire/freeswitch/blob/master/src/switch_ivr_bridge.c

