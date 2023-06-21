"""Base class that all cache classes inherit from."""
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict


class SmartCacheBase(ABC):

    @abstractmethod 
    def add(self, key, value) -> Dict[str, Any]:
        """Adds a key-value pair to the cache."""

    @abstractmethod
    def lookup(self, key) -> Optional[Any]:
        """Looks up a key in the cache."""


