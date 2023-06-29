"""SQL wrapper around SQLDatabase in langchain."""
from typing import Any

from langchain.sql_database import SQLDatabase as LangchainSQLDatabase
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import Engine


class SQLDatabase(LangchainSQLDatabase):
    """SQL Database.

    Wrapper around SQLDatabase object from langchain. Offers
    some helper utilities for insertion and querying.
    See `langchain documentation <https://tinyurl.com/4we5ku8j>`_ for more details:

    Args:
        *args: Arguments to pass to langchain SQLDatabase.
        **kwargs: Keyword arguments to pass to langchain SQLDatabase.

    """

    _uri = ""

    @property
    def engine(self) -> Engine:
        """Return SQL Alchemy engine."""
        return self._engine

    @property
    def metadata_obj(self) -> MetaData:
        """Return SQL Alchemy metadata."""
        return self._metadata

    @property
    def database_uri(self) -> str:
        """Return database uri"""
        return self._uri

    @classmethod
    def from_uri(
        cls, database_uri: str, engine_args: dict | None = None, **kwargs: Any
    ) -> "SQLDatabase":
        """Construct a SQLAlchemy engine from URI."""
        _engine_args = engine_args or {}
        return cls(create_engine(database_uri, **_engine_args), **kwargs)

    @classmethod
    def get_sql_engine(cls) -> "SQLDatabase":
        return cls.from_uri(cls._uri)

    def run_sql(self, command: str) -> tuple[str, dict]:
        """Execute a SQL statement and return a string representing the results.

        If the statement returns rows, a string of the results is returned.
        If the statement returns no rows, an empty string is returned.
        """
        with self._engine.connect() as connection:
            cursor = connection.execute(text(command))
            if cursor.returns_rows:
                result = cursor.fetchall()
                return str(result), {"result": result}
        return "", {}
