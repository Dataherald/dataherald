const { App } = require('@slack/bolt')
const { log } = require('console')
const handleMessage = require('../handlers/message')
require('dotenv').config()

const app = new App({
    token: process.env.SLACK_BOT_ACCESS_TOKEN,
    signingSecret: process.env.SLACK_SIGNING_SECRET,
    socketMode: true,
    appToken: process.env.SLACK_APP_TOKEN,
})

// Listens to incoming messages in direct messages with the bot
app.message(({ message: { text, user }, say }) =>
    handleMessage(text, user, say)
)

// Listens to incoming messages that mention the bot user
app.event('app_mention', ({ event: { text, user }, say }) =>
    handleMessage(text, user, say)
)

async function startServer() {
    const appPort = process.env.PORT || 3000
    await app.start(appPort)

    log(`Dataherald AI Slack client is running on http//:localhost:${appPort}`)
}

startServer()
