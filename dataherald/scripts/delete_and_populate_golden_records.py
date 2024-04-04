import os

import dataherald.config
from dataherald.config import System
from dataherald.db import DB
from dataherald.types import GoldenSQL
from dataherald.vector_store import VectorStore

if __name__ == "__main__":
    settings = dataherald.config.Settings()
    system = System(settings)
    system.start()
    storage = system.instance(DB)
    golden_sql_collection = os.environ.get("GOLDEN_SQL_COLLECTION", "ai-stage")

    golden_sqls = storage.find_all("golden_sqls")
    vector_store = system.instance(VectorStore)
    try:
        vector_store.delete_collection(golden_sql_collection)
    except Exception:  # noqa: S110
        pass
    stored_golden_sqls = []
    for golden_sql_dict in golden_sqls:
        golden_sql = GoldenSQL(**golden_sql_dict, id=str(golden_sql_dict["_id"]))
        stored_golden_sqls.append(golden_sql)
    vector_store.add_records(stored_golden_sqls, golden_sql_collection)
