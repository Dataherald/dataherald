from abc import ABC, abstractmethod
from typing import Any

from dataherald.config import Component, System


class Model(Component, ABC):
    model: Any

    @abstractmethod
    def __init__(self, system: System):
        self.system = system

    @abstractmethod
    def get_model(self, **kwargs: Any) -> Any:
        pass
