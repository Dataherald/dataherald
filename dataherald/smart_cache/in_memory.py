from dataherald.smart_cache.base import SmartCacheBase
from dataherald.config import System
from typing import Any
from overrides import override

class InMemoryCache(SmartCacheBase):
    cache:dict = {} 
    """Test implementation. Just keep everything in memory."""
    def __init__(self, sytstem: System):
        self.cache = {}
    
    @override
    def add(self, key, value) -> dict[str, Any]:
        print('Adding to cache: ', key, value)
        self.cache[key] = value
        return {key: value}
    
    @override
    def lookup(self, key):
        print('Looking up in cache: ', key)
        return self.cache.get(key, None)