from abc import ABC, abstractmethod
from typing import Any, List

from dataherald.api.types import Query
from dataherald.config import Component
from dataherald.eval import Evaluation
from dataherald.sql_database.models.types import SSHSettings
from dataherald.types import DataDefinitionType, NLQueryResponse


class API(Component, ABC):
    @abstractmethod
    def heartbeat(self) -> int:
        """Returns the current server time in nanoseconds to check if the server is alive"""
        pass

    @abstractmethod
    def answer_question(self, question: str, db_alias: str) -> NLQueryResponse:
        pass

    @abstractmethod
    def evaluate_question(self, question: str, golden_sql: str) -> Evaluation:
        pass

    @abstractmethod
    def connect_database(
        self,
        alias: str,
        use_ssh: bool,
        connection_uri: str | None = None,
        ssh_settings: SSHSettings | None = None,
    ) -> bool:
        pass

    @abstractmethod
    def add_golden_records(self, golden_records: List) -> bool:
        pass

    @abstractmethod
    def execute_query(self, query: Query) -> tuple[str, dict]:
        pass
