from dataherald.smart_cache import SmartCache
from dataherald.config import System
from dataherald.types import NLQueryResponse
from typing import Any
from overrides import override
import logging

logger = logging.getLogger(__name__)

class InMemoryCache(SmartCache):
    cache:dict = {} 
    """Test implementation. Just keep everything in memory."""
    def __init__(self, sytstem: System):
        self.cache = {}
    
    @override
    def add(self, key: str, value:NLQueryResponse) -> dict[str, Any]:
        logger.info('Adding to cache: ', key, value)
        self.cache[key] = value
        return {key: value}
    
    @override
    def lookup(self, key: str) -> str:
        return self.cache.get(key, None)