# Slack Bot Client

This is a Slack bot that listens for messages on companies workspaces and interact with our Dataherald AI API

## Building and Running with Docker
We use Docker to create a reproducible environment for the Slackbot.

1. Install dependencies
```
pnpm install
```
> It's not necessary to run docker, but it's good for the IDE to have the packages code available

2. Create your local `.env` file and copy the variables from `.env.example` and fill them up

3. Build the Docker container
```
docker-compose build
```

4. Run the Docker container:
```
docker-compose up
```

## Setting Up Ngrok
You can use Ngrok to expose your local server to the internet so that Slack can interact with our bot when *`socket mode` is off*

[Getting started guidelines](https://ngrok.com/docs/getting-started/)

> You should expose the docker container port you setup

## Local development

Environment variables need to be filled in with the data from the Slackbot app from Slack. We recommend using DEV slackbot for development. Note that to communicate with the Slackbot the `ngrok` URL must be added to the **Request URL** list in the Event Subscriptions tab. Also for installation the Oauth redirect URL must be added.