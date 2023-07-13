const { App } = require('@slack/bolt')
const { log } = require('console')
require('dotenv').config()

const app = new App({
    token: process.env.SLACK_BOT_ACCESS_TOKEN,
    signingSecret: process.env.SLACK_SIGNING_SECRET,
    socketMode: true,
    appToken: process.env.SLACK_APP_TOKEN,
})

const API_URL = process.env.API_URL

// Listens to incoming messages in direct messages with the bot
app.message(async ({ message, say }) => {
    const { user, text: userMessage } = message
    await say({
        blocks: [
            {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `:wave: Hello, <@${user}>. I will look up in your database for an answer to your inquiry. Please, give me a few moments and I'll get back to you.`,
                },
            },
        ],
        text: 'Fallback text for notifications',
    })

    try {
        const query = encodeURIComponent(userMessage)
        const endpointUrl = `${API_URL}/question?question=${query}`
        log('fetching data from', endpointUrl)
        const response = await fetch(endpointUrl, {
            method: 'POST',
            headers: { 'Content-type': 'application/json' },
        })
        const data = await response.json()
        const { nl_response, sql_query, exec_time } = data
        const execTime = parseFloat(exec_time).toFixed(2)

        await say({
            blocks: [
                {
                    type: 'section',
                    text: {
                        type: 'mrkdwn',
                        text: `:mag: *Response*: ${nl_response}`,
                    },
                },
                {
                    type: 'section',
                    text: {
                        type: 'mrkdwn',
                        text: `:memo: *Generated SQL Query*: \n \`\`\`${sql_query}\`\`\``,
                    },
                },
                {
                    type: 'section',
                    text: {
                        type: 'mrkdwn',
                        text: `:stopwatch: *Execution Time*: ${execTime}s`,
                    },
                },
            ],
            text: 'Fallback text for notifications',
        })
    } catch (e) {
        log('Something went wrong: ', e)
        await say({
            blocks: [
                {
                    type: 'section',
                    text: {
                        type: 'mrkdwn',
                        text: ':exclamation: Sorry, something went wrong when I was processing your request. Please try again later.',
                    },
                },
            ],
            text: 'An error occurred',
        })
    }
})

async function startServer() {
    const appPort = process.env.PORT || 3000
    await app.start(appPort)

    log(`Dataherald AI Slack client is running on http//:localhost:${appPort}`)
}

startServer()
