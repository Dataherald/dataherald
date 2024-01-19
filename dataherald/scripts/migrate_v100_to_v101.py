import dataherald.config
from dataherald.config import System
from dataherald.db import DB
from dataherald.utils.encrypt import FernetEncrypt

if __name__ == "__main__":
    settings = dataherald.config.Settings()
    system = System(settings)
    system.start()
    storage = system.instance(DB)
    fernet_encrypt = FernetEncrypt()
    database_connections = storage.find("database_connections", {"use_ssh": True})
    for database_connection in database_connections:
        if "db_driver" not in database_connection["ssh_settings"]:
            continue

        new_uri = f"{database_connection['ssh_settings']['db_driver']}://{database_connection['ssh_settings']['remote_db_name']}:{fernet_encrypt.decrypt(database_connection['ssh_settings']['remote_db_password'])}@{database_connection['ssh_settings']['remote_host']}/{database_connection['ssh_settings']['db_name']}"

        database_connection["uri"] = fernet_encrypt.encrypt(new_uri)
        database_connection["ssh_settings"] = {
            "host": database_connection["ssh_settings"]["host"],
            "username": database_connection["ssh_settings"]["username"],
            "password": database_connection["ssh_settings"]["password"],
            "private_key_password": database_connection["ssh_settings"][
                "private_key_password"
            ],
        }

        storage.update_or_create(
            "database_connections",
            {"_id": database_connection["_id"]},
            database_connection,
        )
