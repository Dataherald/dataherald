import os
from datetime import timedelta

from bson.objectid import ObjectId
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

import dataherald.config
from dataherald.config import System
from dataherald.db import DB
from dataherald.db_scanner.models.types import TableDescriptionStatus
from dataherald.types import GoldenSQL
from dataherald.vector_store import VectorStore


def update_object_id_fields(field_name: str, collection_name: str):
    for obj in storage.find_all(collection_name):
        if (
            obj[field_name]
            and obj[field_name] != ""
            and isinstance(obj[field_name], ObjectId)
        ):
            obj[field_name] = str(obj[field_name])
            storage.update_or_create(collection_name, {"_id": obj["_id"]}, obj)


if __name__ == "__main__":
    settings = dataherald.config.Settings()
    system = System(settings)
    system.start()
    storage = system.instance(DB)
    # Refresh vector stores
    golden_sql_collection = os.environ.get("GOLDEN_RECORD_COLLECTION", "ai-stage")
    vector_store = system.instance(VectorStore)

    golden_records = storage.find_all("golden_records")
    for golden_record in golden_records:
        try:
            storage.insert_one(
                "golden_sqls",
                {
                    "_id": golden_record["_id"],
                    "db_connection_id": str(golden_record["db_connection_id"]),
                    "prompt_text": golden_record["question"],
                    "sql": golden_record["sql_query"],
                },
            )
        except DuplicateKeyError:
            pass
    print("Golden sql remaned...")

    # Change datatype
    update_object_id_fields("db_connection_id", "table_descriptions")
    update_object_id_fields("db_connection_id", "golden_sqls")
    update_object_id_fields("db_connection_id", "instructions")
    update_object_id_fields("db_connection_id", "questions")
    update_object_id_fields("question_id", "responses")
    print("Data types changed...")

    try:
        vector_store.delete_collection(golden_sql_collection)
        print("Vector store deleted...")
    except Exception:  # noqa: S110
        pass
    # Upload golden records
    golden_sqls = storage.find_all("golden_sqls")
    stored_golden_sqls = []
    for golden_sql_dict in golden_sqls:
        golden_sql = GoldenSQL(**golden_sql_dict, id=str(golden_sql_dict["_id"]))
        stored_golden_sqls.append(golden_sql)
    vector_store.add_records(stored_golden_sqls, golden_sql_collection)
    print("Golden sqls uploaded...")

    # Update the table_descriptions status
    for table_description in storage.find_all("table_descriptions"):
        if table_description["status"] == "SYNCHRONIZED":
            table_description["status"] = TableDescriptionStatus.SCANNED.value
        elif table_description["status"] == "NOT_SYNCHRONIZED":
            table_description["status"] = TableDescriptionStatus.NOT_SCANNED.value
        storage.update_or_create(
            "table_descriptions", {"_id": table_description["_id"]}, table_description
        )

    # Migrate questions in prompts collection
    questions = storage.find_all("questions")
    for question in questions:
        responses = storage.find(
            "responses", {"question_id": str(question["_id"])}, [("_id", ASCENDING)]
        )
        try:
            storage.insert_one(
                "prompts",
                {
                    "_id": question["_id"],
                    "db_connection_id": str(question["db_connection_id"]),
                    "text": question["question"],
                    "created_at": (
                        None if len(responses) == 0 else responses[0]["created_at"]
                    ),
                    "metadata": None,
                },
            )
        except DuplicateKeyError:
            continue

        # Migrate responses in sql_questions and nl_questions collections
        for response in responses:
            # create sql_generation
            try:
                storage.insert_one(
                    "sql_generations",
                    {
                        "_id": response["_id"],
                        "prompt_id": str(response["question_id"]),
                        "evaluate": (
                            False if response["confidence_score"] is None else True
                        ),
                        "sql": response["sql_query"],
                        "status": (
                            "VALID"
                            if response["sql_generation_status"] == "VALID"
                            else "INVALID"
                        ),
                        "completed_at": (
                            response["created_at"]
                            + timedelta(seconds=response["exec_time"])
                            if response["exec_time"]
                            else None
                        ),
                        "tokens_used": response["total_tokens"],
                        "confidence_score": response["confidence_score"],
                        "error": response["error_message"],
                        "created_at": response["created_at"],
                        "metadata": None,
                    },
                )
            except DuplicateKeyError:
                continue

            # create nl_genertion
            if response["response"]:
                storage.insert_one(
                    "nl_generations",
                    {
                        "sql_generation_id": str(response["_id"]),
                        "text": response["response"],
                        "created_at": (
                            response["created_at"]
                            + timedelta(seconds=response["exec_time"])
                            if response["exec_time"]
                            else response["created_at"]
                        ),
                        "metadata": None,
                    },
                )
        print("SQL_generations and NL_generations created...")
    print("Prompts created...")
