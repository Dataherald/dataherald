"""Base class that all cache classes inherit from."""

from abc import ABC, abstractmethod
from typing import Any, Union

from dataherald.config import Component
from dataherald.types import Response


class SmartCache(Component, ABC):
    @abstractmethod
    def add(self, key: str, value: Response) -> dict[str, Any]:
        """Adds a key-value pair to the cache."""

    @abstractmethod
    def lookup(self, key: str) -> str:
        """Looks up a key in the cache."""
