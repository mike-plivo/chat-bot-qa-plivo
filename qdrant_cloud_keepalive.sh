#!/bin/bash
#
if [ "$QDRANT_CLOUD_KEEPALIVE" != "true" ]; then
    exit 0
fi

echo "qdrant_cloud_keepalive.sh starting"

while [ 1 ]; do
    echo "qdrant_cloud_keepalive.sh running"
    PY=$(which python3)
    $PY ./qdrant_cloud_keepalive.py  
    ret=$?
    if [ $ret -ne 0 ]; then
	    echo "qdrant_cloud_keepalive.sh failed with code $ret"
    else
        echo "qdrant_cloud_keepalive.sh finished successfully"
    fi
    sleep 300
done

echo "qdrant_cloud_keepalive.sh exiting"
