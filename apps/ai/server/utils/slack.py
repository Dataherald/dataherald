import re

from slack_sdk import WebClient

from modules.query.models.entities import QueryRef
from modules.query.models.responses import CoreQueryResponse


class SlackWebClient:
    def __init__(self, slack_bot_access_token):
        # xoxb-* token (required)
        self.client = WebClient(token=slack_bot_access_token)

    def get_user_real_name(self, user_id: str) -> str:
        user = self.client.users_info(user=user_id).get("user")
        if user and "real_name" in user:
            return user["real_name"]
        return "unknown_user"

    def send_message(self, channel_id: str, thread_ts: str, message: str):
        self.client.chat_postMessage(
            channel=channel_id, thread_ts=thread_ts, text=message
        )

    def send_verified_query_message(
        self,
        query_ref: QueryRef,
        query_response: CoreQueryResponse,
        question: str,
    ):
        message_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":wave: Hello, <@{query_ref.slack_info.user_id}>! Your query {query_ref.display_id} has been verified.",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Question: {question}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Response: {query_response.nl_response}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":memo: *Generated SQL Query*: \n ```{query_response.sql_query}```",
                },
            },
        ]
        self.client.chat_postMessage(
            channel=query_ref.slack_info.channel_id,
            thread_ts=query_ref.slack_info.thread_ts,
            blocks=message_blocks,
        )


def remove_slack_mentions(text: str) -> str:
    slack_user_mention_pattern = r"<@(.*?)>"
    slack_team_mention_pattern = r"<!(.*?)>"
    slack_channel_mention_pattern = r"<#(.*?)>"
    return re.sub(
        slack_channel_mention_pattern,
        "",
        re.sub(
            slack_team_mention_pattern,
            "",
            re.sub(slack_user_mention_pattern, "", text),
        ).lstrip(),
    )
