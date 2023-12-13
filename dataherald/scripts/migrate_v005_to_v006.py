import dataherald.config
from dataherald.config import System
from dataherald.db import DB


def update_object_id_fields(field_name: str, collection_name: str):
    for obj in storage.find_all(collection_name):
        if obj[field_name] and obj[field_name] != "":
            obj[field_name] = str(obj[field_name])
            storage.update_or_create(collection_name, {"_id": obj["_id"]}, obj)


if __name__ == "__main__":
    settings = dataherald.config.Settings()
    system = System(settings)
    system.start()
    storage = system.instance(DB)

    # Change datatype
    update_object_id_fields("db_connection_id", "table_descriptions")
    update_object_id_fields("db_connection_id", "golden_records")
    update_object_id_fields("db_connection_id", "questions")
    update_object_id_fields("db_connection_id", "instructions")
    update_object_id_fields("question_id", "responses")
