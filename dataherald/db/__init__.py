from abc import ABC, abstractmethod
from dataherald.config import Component
from dataherald.config import System


class DB(Component, ABC):
    @abstractmethod
    def __init__(self, system: System):
        self.system = system