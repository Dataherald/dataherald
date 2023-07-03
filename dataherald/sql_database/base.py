"""SQL wrapper around SQLDatabase in langchain."""
from typing import Any, List

from langchain.sql_database import SQLDatabase as LangchainSQLDatabase
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import Engine
from sshtunnel import SSHTunnelForwarder

from dataherald.config import SSHSettings


class SQLDatabase(LangchainSQLDatabase):
    """SQL Database.

    Wrapper around SQLDatabase object from langchain. Offers
    some helper utilities for insertion and querying.
    See `langchain documentation <https://tinyurl.com/4we5ku8j>`_ for more details:

    Args:
        *args: Arguments to pass to langchain SQLDatabase.
        **kwargs: Keyword arguments to pass to langchain SQLDatabase.

    """

    _uri: str | None = None
    _ssh: SSHSettings = SSHSettings()

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
        if cls._ssh.enabled:
            return cls.from_uri_ssh()
        return cls.from_uri(cls._uri)

    @classmethod
    def from_uri_ssh(cls):
        ssh = cls._ssh
        database = "v2_real_estate"
        server = SSHTunnelForwarder(
            (ssh.host, 22),
            ssh_username=ssh.username,
            ssh_password=ssh.password,
            remote_bind_address=(ssh.remote_host, 5432),
        )
        server.start()
        local_port = str(server.local_bind_port)
        local_host = str(server.local_bind_host)
        return cls.from_uri(
            f"postgresql+psycopg2://{ssh.remote_db_name}:{ssh.remote_db_password}@{local_host}:{local_port}/{database}"
        )

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

    # from llama-index's sql-wrapper
    def get_table_columns(self, table_name: str) -> List[Any]:
        """Get table columns."""
        return self._inspector.get_columns(table_name)

    # from llama-index's sql-wrapper
    def get_single_table_info(self, table_name: str) -> str:
        """Get table info for a single table."""
        # same logic as table_info, but with specific table names
        template = (
            "Table '{table_name}' has columns: {columns} "
            "and foreign keys: {foreign_keys}."
        )
        columns = []
        for column in self._inspector.get_columns(table_name):
            columns.append(f"{column['name']} ({str(column['type'])})")
        column_str = ", ".join(columns)
        foreign_keys = []
        for foreign_key in self._inspector.get_foreign_keys(table_name):
            foreign_keys.append(
                f"{foreign_key['constrained_columns']} -> "
                f"{foreign_key['referred_table']}.{foreign_key['referred_columns']}"
            )
        foreign_key_str = ", ".join(foreign_keys)
        return template.format(
            table_name=table_name, columns=column_str, foreign_keys=foreign_key_str
        )
