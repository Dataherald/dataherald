from posthog import Posthog

from config import analytic_settings


class Analytics:
    def __init__(self):
        self.posthog = Posthog(
            analytic_settings.posthog_api_key, host=analytic_settings.posthog_host
        )
        if analytic_settings.posthog_disabled:
            self.posthog.disabled = True

    def track(self, user_id: str, event: str, properties: dict):
        self.posthog.capture(
            user_id,
            event,
            properties=properties,
        )

    def identify(self, user_id: str, properties: dict):
        self.posthog.identify(
            user_id,
            properties=properties,
        )

    def track_error(
        self,
        user_id: str,
        path: str,
    ):
        self.track(
            user_id,
            "engine_error",
            {
                "path": path,
            },
        )
