import os

from sql_metadata import Parser

import dataherald.config
from dataherald.config import System
from dataherald.db import DB
from dataherald.vector_store import VectorStore


def add_db_connection_id(collection_name: str, storage) -> None:
    collection_rows = storage.find_all(collection_name)
    for collection_row in collection_rows:
        if "db_alias" not in collection_row:
            continue
        database_connection = storage.find_one(
            "database_connection", {"alias": collection_row["db_alias"]}
        )
        if not database_connection:
            continue
        collection_row["db_connection_id"] = str(database_connection["_id"])
        # update object
        storage.update_or_create(
            collection_name, {"_id": collection_row["_id"]}, collection_row
        )


if __name__ == "__main__":
    settings = dataherald.config.Settings()
    system = System(settings)
    system.start()
    storage = system.instance(DB)
    # Update relations
    add_db_connection_id("table_schema_detail", storage)
    add_db_connection_id("golden_records", storage)
    add_db_connection_id("nl_question", storage)
    # Refresh vector stores
    golden_record_collection = os.environ.get("GOLDEN_SQL_COLLECTION", "ai-stage")
    vector_store = system.instance(VectorStore)
    try:
        vector_store.delete_collection(golden_record_collection)
    except Exception:  # noqa: S110
        pass
    # Upload golden records
    golden_records = storage.find_all("golden_records")
    for golden_record in golden_records:
        tables = Parser(golden_record["sql_query"]).tables
        if len(tables) == 0:
            tables = [""]
        question = golden_record["question"]
        vector_store.add_record(
            documents=question,
            db_connection_id=golden_record["db_connection_id"],
            collection=golden_record_collection,
            metadata=[
                {
                    "tables_used": tables[0],
                    "db_connection_id": golden_record["db_connection_id"],
                }
            ],  # this should be updated for multiple tables
            ids=[str(golden_record["_id"])],
        )
    # Re-name collections
    try:
        storage.rename("nl_query_response", "nl_query_responses")
        storage.rename("nl_question", "nl_questions")
        storage.rename("database_connection", "database_connections")
        storage.rename("table_schema_detail", "table_descriptions")
    except Exception:  # noqa: S110
        pass
