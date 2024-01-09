require('dotenv').config()
const { log, error } = require('console')
const getApiAuthToken = require('../auth')
const API_URL = process.env.API_URL

const SOCKET_MODE = {
    signingSecret: process.env.SLACK_SIGNING_SECRET,
    socketMode: true,
    appToken: process.env.SLACK_APP_TOKEN,
    token: process.env.SLACK_BOT_ACCESS_TOKEN,
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
}

const OAUTH_CONFIG = {
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
                    `${API_URL}/organizations/slack/installation`,
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
                    `${API_URL}/organizations/slack/installation?workspace_id=${installQuery.teamId}`,
                    {
                        headers: {
                            Authorization: `Bearer ${apiToken}`,
                        },
                    }
                )
                return await response.json()
            } catch (e) {
                error('Failed fetching organization token: ', e)
            }
        },
        deleteInstallation: async () => {},
    },
}

module.exports = {
    SOCKET_MODE,
    OAUTH_CONFIG,
}
