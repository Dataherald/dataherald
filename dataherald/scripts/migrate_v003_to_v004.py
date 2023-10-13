from datetime import datetime

from bson.objectid import ObjectId

import dataherald.config
from dataherald.config import System
from dataherald.db import DB


def update_object_id_fields(field_name: str, collection_name: str):
    for obj in storage.find_all(collection_name):
        if obj[field_name] and obj[field_name] != "":
            obj[field_name] = ObjectId(obj[field_name])
            storage.update_or_create(collection_name, {"_id": obj["_id"]}, obj)


if __name__ == "__main__":
    settings = dataherald.config.Settings()
    system = System(settings)
    system.start()
    storage = system.instance(DB)

    # Rename collections
    try:
        storage.rename("nl_questions", "questions")
        storage.rename("nl_query_responses", "responses")
    except Exception:  # noqa: S110
        pass

    # Rename fields
    storage.rename_field("responses", "nl_question_id", "question_id")
    storage.rename_field("responses", "nl_response", "response")

    # Add field
    for response in storage.find_all("responses"):
        if "created_at" not in response:
            response["created_at"] = datetime.now()
            storage.update_or_create("responses", {"_id": response["_id"]}, response)

    # Change datatype
    update_object_id_fields("db_connection_id", "table_descriptions")
    update_object_id_fields("db_connection_id", "golden_records")
    update_object_id_fields("db_connection_id", "questions")
    update_object_id_fields("db_connection_id", "instructions")
    update_object_id_fields("question_id", "responses")
