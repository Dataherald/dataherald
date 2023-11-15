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
    golden_record_collection = os.environ.get(
        "GOLDEN_RECORD_COLLECTION", "dataherald-staging"
    )

    vector_store = system.instance(VectorStore)
    try:
        vector_store.delete_collection(golden_record_collection)
    except Exception:  # noqa: S110
        pass
    golden_records = storage.find_all("golden_records")
    for golden_record in golden_records:
        tables = Parser(golden_record["sql_query"]).tables
        if len(tables) == 0:
            tables = [""]
        question = golden_record["question"]
        vector_store.add_record(
            documents=question,
            db_connection_id=str(golden_record["db_connection_id"]),
            collection=golden_record_collection,
            metadata=[
                {
                    "tables_used": tables[0],
                    "db_connection_id": str(golden_record["db_connection_id"]),
                }
            ],
            ids=[str(golden_record["_id"])],
        )
