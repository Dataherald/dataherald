require('dotenv').config()
const { App } = require('@slack/bolt')
const { SOCKET_MODE, OAUTH_CONFIG } = require('../config')
const { log, error } = require('console')
const handleMessage = require('../handlers/message')

const appConfig =
    process.env.SOCKET_MODE === 'true' ? SOCKET_MODE : OAUTH_CONFIG

const app = new App(appConfig)

// Listens to incoming messages that mention the bot user
app.event('app_mention', ({ event, say }) => handleMessage(event, say))

async function startServer() {
    const appPort = process.env.PORT || 3000
    await app.start(appPort)

    try {
        await fetch(`${process.env.API_URL}/heartbeat`)
        log(`Dataherald AI Slack client is running on port ${appPort}`)
    } catch {
        error(`Couldn't connect to ${process.env.API_URL}`)
    }
}

startServer()
