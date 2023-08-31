require('dotenv').config()
const { log } = require('console')

const API_URL = process.env.API_URL

async function handleMessage(context, say) {
    const {
        text: message,
        channel: channel_id,
        user: userId,
        ts: thread_ts,
        team: teamId,
    } = context
    log(
        `Slack message "${message}" received from ${userId} in channel ${channel_id} (thread: ${thread_ts}) that belongs to ${teamId} workspace`
    )

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
        const endpointUrl = `${API_URL}/k2/question`
        const payload = {
            question: message,
            slack_user_id: userId,
            slack_workspace_id: teamId,
            slack_channel_id: channel_id,
            slack_thread_ts: thread_ts,
        }
        log('Fetching data from', endpointUrl)
        log('Request payload:', payload)
        const response = await fetch(endpointUrl, {
            method: 'POST',
            headers: { 'Content-type': 'application/json' },
            body: JSON.stringify(payload),
        })
        const data = await response.json()
        const {
            nl_response,
            sql_query,
            exec_time,
            display_id,
            above_confidence_threshold,
        } = data
        const execTime = parseFloat(exec_time).toFixed(2)

        if (above_confidence_threshold) {
            await say({
                blocks: [
                    {
                        type: 'section',
                        text: {
                            type: 'mrkdwn',
                            text: `:mag: *Response*: ${nl_response}`,
                        },
                    },
                    ...(sql_query
                        ? [
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
                          ]
                        : []),
                ],
                text: 'Fallback text for notifications',
                thread_ts,
            })
        } else {
            await say({
                blocks: [
                    {
                        type: 'section',
                        text: {
                            type: 'mrkdwn',
                            text: `Sorry, the generated response ${display_id} did not exceed the confidence threshold. We will return the response once it has been verified by the data-team admin.`,
                        },
                    },
                ],
                text: 'Fallback text for notifications',
                thread_ts,
            })
        }
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
