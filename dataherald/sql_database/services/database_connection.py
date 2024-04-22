import re

from sqlalchemy import inspect

from dataherald.db import DB
from dataherald.db_scanner import Scanner
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.repositories.database_connections import DatabaseConnectionRepository
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import DatabaseConnectionRequest
from dataherald.utils.encrypt import FernetEncrypt
from dataherald.utils.error_codes import CustomError


class SchemaNotSupportedError(CustomError):
    pass


class DatabaseConnectionService:
    def __init__(self, scanner: Scanner, storage: DB):
        self.scanner = scanner
        self.storage = storage

    def get_sql_database(
        self, database_connection: DatabaseConnection, schema: str = None
    ) -> SQLDatabase:
        fernet_encrypt = FernetEncrypt()
        if schema:
            database_connection.connection_uri = fernet_encrypt.encrypt(
                self.add_schema_in_uri(
                    fernet_encrypt.decrypt(database_connection.connection_uri),
                    schema,
                    database_connection.dialect.value,
                )
            )
        return SQLDatabase.get_sql_engine(database_connection, True)

    def get_current_schema(
        self, database_connection: DatabaseConnection
    ) -> list[str] | None:
        sql_database = SQLDatabase.get_sql_engine(database_connection, True)
        inspector = inspect(sql_database.engine)
        if inspector.default_schema_name and database_connection.dialect not in [
            "mssql",
            "mysql",
            "clickhouse",
            "duckdb",
        ]:
            return [inspector.default_schema_name]
        if database_connection.dialect == "bigquery":
            pattern = r"([^:/]+)://([^/]+)/([^/]+)(\?[^/]+)"
            match = re.match(pattern, str(sql_database.engine.url))
            if match:
                return [match.group(3)]
        elif database_connection.dialect == "databricks":
            pattern = r"&schema=([^&]*)"
            match = re.search(pattern, str(sql_database.engine.url))
            if match:
                return [match.group(1)]
        return None

    def remove_schema_in_uri(self, connection_uri: str, dialect: str) -> str:
        if dialect in ["snowflake"]:
            pattern = r"([^:/]+)://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/([^/]+)"
            match = re.match(pattern, connection_uri)
            if match:
                return match.group(0)
        if dialect in ["bigquery"]:
            pattern = r"([^:/]+)://([^/]+)"
            match = re.match(pattern, connection_uri)
            if match:
                return match.group(0)
        elif dialect in ["databricks"]:
            pattern = r"&schema=[^&]*"
            return re.sub(pattern, "", connection_uri)
        elif dialect in ["postgresql"]:
            pattern = r"\?options=-csearch_path" r"=[^&]*"
            return re.sub(pattern, "", connection_uri)
        return connection_uri

    def add_schema_in_uri(self, connection_uri: str, schema: str, dialect: str) -> str:
        connection_uri = self.remove_schema_in_uri(connection_uri, dialect)
        if dialect in ["snowflake", "bigquery"]:
            return f"{connection_uri}/{schema}"
        if dialect in ["databricks"]:
            return f"{connection_uri}&schema={schema}"
        if dialect in ["postgresql"]:
            return f"{connection_uri}?options=-csearch_path={schema}"
        return connection_uri

    def create(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> DatabaseConnection:
        database_connection = DatabaseConnection(
            alias=database_connection_request.alias,
            connection_uri=database_connection_request.connection_uri.strip(),
            schemas=database_connection_request.schemas,
            path_to_credentials_file=database_connection_request.path_to_credentials_file,
            llm_api_key=database_connection_request.llm_api_key,
            use_ssh=database_connection_request.use_ssh,
            ssh_settings=database_connection_request.ssh_settings,
            file_storage=database_connection_request.file_storage,
            metadata=database_connection_request.metadata,
        )
        if database_connection.schemas and database_connection.dialect in [
            "redshift",
            "awsathena",
            "mssql",
            "mysql",
            "clickhouse",
            "duckdb",
        ]:
            raise SchemaNotSupportedError(
                "Schema not supported for this db",
                description=f"The {database_connection.dialect} dialect doesn't support schemas",
            )
        if not database_connection.schemas:
            database_connection.schemas = self.get_current_schema(database_connection)

        schemas_and_tables = {}
        fernet_encrypt = FernetEncrypt()

        if database_connection.schemas:
            for schema in database_connection.schemas:
                database_connection.connection_uri = fernet_encrypt.encrypt(
                    self.add_schema_in_uri(
                        database_connection_request.connection_uri.strip(),
                        schema,
                        str(database_connection.dialect),
                    )
                )
                sql_database = SQLDatabase.get_sql_engine(database_connection, True)
                schemas_and_tables[schema] = sql_database.get_tables_and_views()
        else:
            sql_database = SQLDatabase.get_sql_engine(database_connection, True)
            schemas_and_tables[None] = sql_database.get_tables_and_views()

        # Connect db
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        database_connection.connection_uri = fernet_encrypt.encrypt(
            self.remove_schema_in_uri(
                database_connection_request.connection_uri.strip(),
                str(database_connection.dialect),
            )
        )
        db_connection = db_connection_repository.insert(database_connection)

        scanner_repository = TableDescriptionRepository(self.storage)
        # Add created tables
        for schema, tables in schemas_and_tables.items():
            self.scanner.create_tables(
                tables, str(db_connection.id), schema, scanner_repository
            )
        return DatabaseConnection(**db_connection.dict())
