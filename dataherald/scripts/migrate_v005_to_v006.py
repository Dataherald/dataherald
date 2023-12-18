import os

from sql_metadata import Parser

import dataherald.config
from dataherald.config import System
from dataherald.db import DB
from dataherald.vector_store import VectorStore

if __name__ == "__main__":
    settings = dataherald.config.Settings()
    system = System(settings)
    system.start()
    storage = system.instance(DB)
    # Refresh vector stores
    golden_sql_collection = os.environ.get(
        "GOLDEN_SQL_COLLECTION", "dataherald-staging"
    )
    vector_store = system.instance(VectorStore)

    try:
        # Re-name collections
        storage.rename("golden_records", "golden_sqls")
        # Rename fields
        storage.rename_field("golden_sqls", "sql_query", "sql")
        storage.rename_field("golden_sqls", "question", "prompt_text")
    except Exception:  # noqa: S110
        pass

    try:
        vector_store.delete_collection(golden_sql_collection)
    except Exception:  # noqa: S110
        pass
    # Upload golden records
    golden_sqls = storage.find_all("golden_sqls")
    for golden_sql in golden_sqls:
        tables = Parser(golden_sql["sql"]).tables
        if len(tables) == 0:
            tables = [""]
        prompt_text = golden_sql["prompt_text"]
        vector_store.add_record(
            documents=prompt_text,
            db_connection_id=str(golden_sql["db_connection_id"]),
            collection=golden_sql_collection,
            metadata=[
                {
                    "tables_used": tables[0],
                    "db_connection_id": str(golden_sql["db_connection_id"]),
                }
            ],  # this should be updated for multiple tables
            ids=[str(golden_sql["_id"])],
        )
