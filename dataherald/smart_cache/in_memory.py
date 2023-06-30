import logging
from typing import Any
from dataherald.config import Settings

from overrides import override

from dataherald.smart_cache import SmartCache
from dataherald.types import NLQueryResponse

logger = logging.getLogger(__name__)


class InMemoryCache(SmartCache):
    cache: dict = {}
    """Test implementation. Just keep everything in memory."""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.cache = {}

    @override
    def add(self, key: str, value: NLQueryResponse) -> dict[str, Any]:
        logger.info(f"Adding to cache: {value.dict()}")
        self.cache[key] = value
        return {key: value}

    @override
    def lookup(self, key: str) -> str:
        return self.cache.get(key, None)
