import dataherald.config
from dataherald.config import System
from dataherald.db import DB
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.utils.encrypt import FernetEncrypt

if __name__ == "__main__":
    settings = dataherald.config.Settings()
    system = System(settings)
    system.start()
    storage = system.instance(DB)
    fernet_encrypt = FernetEncrypt()
    database_connections = storage.find_all("database_connections")
    for database_connection in database_connections:
        if not database_connection.get("dialect"):
            decrypted_uri = fernet_encrypt.decrypt(
                database_connection["connection_uri"]
            )
            dialect_prefix = DatabaseConnection.get_dialect(decrypted_uri)
            dialect = DatabaseConnection.set_dialect(dialect_prefix)
            storage.update_or_create(
                "database_connections",
                {"_id": database_connection["_id"]},
                {"dialect": dialect},
            )
