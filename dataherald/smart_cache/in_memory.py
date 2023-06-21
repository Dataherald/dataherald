from dataherald.smart_cache.base import SmartCacheBase


class InMemoryCache(SmartCacheBase):
    """Smart cache that uses Redis as a backend."""
    def __init__(self):
        self.cache = {}
    
    def add(self, key, value):
        self.cache[key] = value
    
    def lookup(self, key):
        return self.cache.get(key, None)