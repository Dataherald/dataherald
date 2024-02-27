require('dotenv').config()
const { log, error } = require('console')
const getApiAuthToken = require('../../auth')

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
    const welcomeMessage = `Hey there! Please, give me a few moments and I'll be back with your answer.`
    await say({
        blocks: [
            {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `:wave: ${welcomeMessage}`,
                },
            },
        ],
        text: welcomeMessage,
        thread_ts,
    })

    try {
        const apiToken = await getApiAuthToken()
        const endpointUrl = `${API_URL}/generations`
        const payload = {
            prompt: message,
            slack_info: {
                user_id: userId,
                workspace_id: teamId,
                channel_id: channel_id,
                thread_ts: thread_ts,
            },
        }
        log('Fetching data from', endpointUrl)
        log('Request payload:', payload)
        const response = await fetch(endpointUrl, {
            method: 'POST',
            headers: {
                'Content-type': 'application/json',
                Authorization: `Bearer ${apiToken}`,
            },
            body: JSON.stringify(payload),
        })
        if (!response.ok) {
            try {
                const { error_code, message, detail } = await response.json()
                error(
                    `API Response not ok: status code ${response.status}, ${response.statusText}, error code: ${error_code}, error message: ${message}, detail: ${detail}`
                )
                const responseMessage = `:warning: Sorry, something went wrong while generating response. Error message: \`${message}\``
                await say({
                    blocks: [
                        {
                            type: 'section',
                            text: {
                                type: 'mrkdwn',
                                text: responseMessage,
                            },
                        },
                    ],
                    text: responseMessage,
                    thread_ts,
                })
            } catch (e) {
                error(
                    'API Response not ok: ',
                    response.status,
                    response.statusText
                )
                const responseMessage = `Sorry, something went wrong when I was processing your request. Please try again later.`
                await say({
                    blocks: [
                        {
                            type: 'section',
                            text: {
                                type: 'mrkdwn',
                                text: `:exclamation: ${responseMessage}`,
                            },
                        },
                    ],
                    text: responseMessage,
                    thread_ts,
                })
            }
        } else {
            const data = await response.json()
            const {
                nl_generation_text: response_message,
                sql,
                exec_time,
                display_id,
                is_above_confidence_threshold,
            } = data
            const execTime = parseFloat(exec_time).toFixed(2)

            if (is_above_confidence_threshold) {
                await say({
                    blocks: [
                        {
                            type: 'section',
                            text: {
                                type: 'mrkdwn',
                                text: `:mag: *Response*: ${response_message}`,
                            },
                        },
                        ...(sql
                            ? [
                                  {
                                      type: 'section',
                                      text: {
                                          type: 'mrkdwn',
                                          text: `:memo: *Generated SQL Query*: \n \`\`\`${sql}\`\`\``,
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
                    text: response_message,
                    thread_ts,
                })
            } else {
                const responseMessage = `The generated response ${display_id} is queued for human verification because it did not exceed the confidence threshold. We'll get back to you once it's been reviewed by the data-team admins.`
                await say({
                    blocks: [
                        {
                            type: 'section',
                            text: {
                                type: 'mrkdwn',
                                text: `:mag: :bust_in_silhouette: ${responseMessage} :hourglass_flowing_sand:`,
                            },
                        },
                    ],
                    text: responseMessage,
                    thread_ts,
                })
            }
        }
    } catch (e) {
        log('Something went wrong: ', e)
        const responseMessage = `Sorry, something went wrong when I was processing your request. Please try again later.`
        await say({
            blocks: [
                {
                    type: 'section',
                    text: {
                        type: 'mrkdwn',
                        text: `:exclamation: ${responseMessage}`,
                    },
                },
            ],
            text: responseMessage,
            thread_ts,
        })
    }
}

module.exports = handleMessage
