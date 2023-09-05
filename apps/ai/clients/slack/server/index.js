const { App } = require('@slack/bolt')
const { log, error } = require('console')
const handleMessage = require('../handlers/message')
const getApiAuthToken = require('../auth')
require('dotenv').config()

const API_URL = process.env.API_URL

const app = new App({
    signingSecret: process.env.SLACK_SIGNING_SECRET,
    clientId: process.env.SLACK_CLIENT_ID,
    clientSecret: process.env.SLACK_CLIENT_SECRET,
    stateSecret: process.env.SLACK_STATE_SECRET,
    scopes: [
        'app_mentions:read',
        'channels:history',
        'channels:read',
        'chat:write',
        'groups:history',
        'groups:read',
        'im:history',
        'im:read',
        'im:write',
        'mpim:history',
        'users:read',
    ],
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
    installerOptions: {
        directInstall: true,
    },
    installationStore: {
        storeInstallation: async (installation) => {
            log('Installing app: ', installation)
            const apiToken = await getApiAuthToken()
            log('Successfully retrieved API token')
            if (installation.team !== undefined) {
                // single team app installation
                return await fetch(
                    `${API_URL}/organization/slack/installation`,
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            Authorization: `Bearer ${apiToken}`,
                        },
                        body: JSON.stringify(installation),
                    }
                )
            }
            throw new Error('Failed saving organization token')
        },
        fetchInstallation: async (installQuery) => {
            log('Fetching app installation: ', installQuery)
            try {
                const apiToken = await getApiAuthToken()
                const response = await fetch(
                    `${API_URL}/organization/slack/installation?workspace_id=${installQuery.teamId}`,
                    {
                        headers: {
                            Authorization: `Bearer ${apiToken}`,
                        },
                    }
                )
                return await response.json()
            } catch (error) {
                error('Failed fetching organization token: ', error)
            }
        },
        deleteInstallation: async () => {},
    },
})

// Listens to incoming messages in direct messages with the bot
app.message(({ message, say }) => handleMessage(message, say))

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
