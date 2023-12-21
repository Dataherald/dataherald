from modules.key.models.entities import BaseKey


class KeyPreviewResponse(BaseKey):
    pass


class KeyResponse(BaseKey):
    api_key: str | None
