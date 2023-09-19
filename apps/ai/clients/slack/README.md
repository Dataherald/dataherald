# Slack Bot Client

This is a Slackbot that listens for messages on the company’s workspaces and interacts with our Dataherald AI API

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

The proper environment variables need to be set in order to develop locally. We recommend using **Dataherald AI [DEV]** slackbot for development and not the **Dataherald AI [STAGE]**. 

There are two ways to develop:
1. Socket mode
2. Oauth mode 

### Socket Mode
This is the **default** for **Dataherald AI [DEV]** Slackbot. It makes a direct connection with our Dataherald workspace to start asking questions. It doesn't support working with other workspaces nor Organizations.

### Oauth Mode
This is the production-like mode in which we're able to install the slackbot in several workspaces and work dynamically with all of them. To be able to use this mode for development its required to:
1. Disable the socket mode on **Dataherald AI [DEV]** 
2. Setup ngork to expose your local server to the internet with SSL certificate.
3. Add the https to the **Redirect URL** list in the **Oauth & permissions** tab
4. Set the https **Request URL** in the **Event Subscriptions** tab. 

> It can't be more than one developer working with the bot