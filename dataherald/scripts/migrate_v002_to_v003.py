import dataherald.config
from dataherald.config import System
from dataherald.db import DB

if __name__ == "__main__":
    settings = dataherald.config.Settings()
    system = System(settings)
    system.start()
    storage = system.instance(DB)
    # Update table_descriptions status
    collection_rows = storage.find_all("table_descriptions")
    for collection_row in collection_rows:
        collection_row["status"] = "SYNCHRONIZED"
        # update object
        storage.update_or_create(
            "table_descriptions", {"_id": collection_row["_id"]}, collection_row
        )
