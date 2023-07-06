# Requirements
## Setup Qdrant cloud
*Sign-in or sign-up at https://cloud.qdrant.io/
*Create a free 1GB cluster
*Note down the Qdrant API key and the Qdrant Cluster Url

## Setup OpenAI
*Sign-in or sign-up  at https://openai.com/
*Setup your account with enough credits
*Note down the OpenAI API key

## Slack bot setup
*You need to be a Slack admin for your workspace. 
*Go to https://api.slack.com/apps and click on “Create a new app”, select “From scratch” in the popup window, and choose a name (for me, it is “PlivoAskMe”), then click on “Create App”.
*Click on “New Slack Commands” and point it to your application API hosted on fly.io (you can do that later if the fly.io application is not online yet)
*From the left menu, click on “OAuth & Permissions” then in the “Bot Token Scopes” section, click on “Add an Oauth scope” and select “commands”
*Go back to the “Basic information” section in the left menu and click “Install to workspace”
*You should be able to see the “App Credentials” section.
*Note down the Slack "Verification Token"

# Fly.io deployment
## Setup the application
Login into your fly.io account and create the application.

Copy the fly.toml example file
```bash
cp fly.toml.example fly.toml # adjust the settings based on your application (name and region)
```

Configure the "app", "primnary_region", "OPENAI_MODEL", and "VECTOR_DATABASE" settings.


## Configure secrets
```bash
fly secrets QDRANT_API_KEY=xxxx # replace 'xxxx' with your Qdrant API key
fly secrets OPENAI_API_KEY=xxxx # replace 'xxxx' with your OpenAI API key
fly secrets SLACK_TOKEN_ID=xxxx # replace 'xxxx' with your Slack Verification token
```

## Deploy the app and machine
```bash
fly deploy --force-machines --local-only --region iad --vm-size shared-cpu-2x
```

## Append data to the vector database
```bash
fly scale memory 4096 # scale up memory to ingest the data
fly ssh console --pty -C 'python3 /app/ingest.py' # collect and inject data into the vector database
fly scale memory 2048 # scale down memory
```

# Update the app
```bash
fly deploy --local-only
```

