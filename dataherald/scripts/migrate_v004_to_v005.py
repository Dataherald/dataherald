import dataherald.config
from dataherald.config import System
from dataherald.db import DB

if __name__ == "__main__":
    settings = dataherald.config.Settings()
    system = System(settings)
    system.start()
    storage = system.instance(DB)

    for db_connection in storage.find_all("database_connections"):
        if "llm_credentials" in db_connection and db_connection["llm_credentials"]:
            db_connection["llm_api_key"] = db_connection["llm_credentials"]["api_key"]
            db_connection["llm_credentials"] = None
            storage.update_or_create(
                "database_connections", {"_id": db_connection["_id"]}, db_connection
            )
