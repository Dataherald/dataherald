require('dotenv').config()
const { log } = require('console')

const API_URL = process.env.API_URL

async function handleMessage(context, say) {
    const { text: message, user, ts: thread_ts } = context
    log('Slack message received', message)
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
        thread_ts,
    })

    try {
        const query = encodeURIComponent(message)
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
