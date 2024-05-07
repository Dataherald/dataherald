import re

from slack_sdk import WebClient


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
