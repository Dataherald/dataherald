"""Base class that all cache classes inherit from."""
from abc import ABC, abstractmethod
from typing import Any

from dataherald.config import Component
from dataherald.types import NLQueryResponse


class SmartCache(Component, ABC):
    @abstractmethod
    def add(self, key: str, value: NLQueryResponse) -> dict[str, Any]:
        """Adds a key-value pair to the cache."""

    @abstractmethod
    def lookup(self, key: str) -> Any | None:
        """Looks up a key in the cache."""
