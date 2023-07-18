const { App } = require('@slack/bolt')
const { log } = require('console')
const handleMessage = require('../handlers/message')
require('dotenv').config()

const app = new App({
    token: process.env.SLACK_BOT_ACCESS_TOKEN,
    signingSecret: process.env.SLACK_SIGNING_SECRET,
    socketMode: process.env.SLACK_SOCKET_MODE === 'true', // default is false
    appToken: process.env.SLACK_APP_TOKEN,
    customRoutes: [
        {
            path: '/health-check',
            method: ['GET'],
            handler: (req, res) => {
                res.writeHead(200)
                res.end(`Things are going just fine at ${req.headers.host}!`)
            },
        },
    ],
})

// Listens to incoming messages in direct messages with the bot
app.message(({ message, say }) =>
    handleMessage(message, say)
)

// Listens to incoming messages that mention the bot user
app.event('app_mention', ({ event, say }) =>
    handleMessage(event, say)
)

async function startServer() {
    const appPort = process.env.PORT || 3000
    await app.start(appPort)

    log(`Dataherald AI Slack client is running on port ${appPort}`)
}

startServer()
