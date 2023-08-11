require('dotenv').config()
const { log } = require('console')

const API_URL = process.env.API_URL

async function handleMessage(context, say, getUserInfo) {
    const { text: message, user: userId, ts: thread_ts } = context
    log(`Slack message "${message}" received from user ${userId}`)

    await say({
        blocks: [
            {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `:wave: Hello, <@${userId}>. I will look up in your database for an answer to your inquiry. Please, give me a few moments and I'll get back to you.`,
                },
            },
        ],
        text: 'Fallback text for notifications',
        thread_ts,
    })

    try {
        const userInfo = await getUserInfo({ user: userId })
        const endpointUrl = `${API_URL}/k2/question`
        log('fetching data from', endpointUrl)
        const response = await fetch(endpointUrl, {
            method: 'POST',
            headers: { 'Content-type': 'application/json' },
            body: JSON.stringify({
                question: message,
                user: {
                    slack_id: userId,
                    username: userInfo.user.real_name
                }
            })
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
            thread_ts,
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
            thread_ts,
        })
    }
}

module.exports = handleMessage
