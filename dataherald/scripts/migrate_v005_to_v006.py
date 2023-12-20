import os
from datetime import timedelta

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError
from sql_metadata import Parser

import dataherald.config
from dataherald.config import System
from dataherald.db import DB
from dataherald.vector_store import VectorStore


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
    # Refresh vector stores
    golden_sql_collection = os.environ.get(
        "GOLDEN_SQL_COLLECTION", "dataherald-staging"
    )
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
    update_object_id_fields("question_id", "responses")
    update_object_id_fields("db_connection_id", "questions")
    print("Data types changed...")

    try:
        vector_store.delete_collection(golden_sql_collection)
        print("Vector store deleted...")
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
    print("Golden sqls uploaded...")

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
                    "created_at": None
                    if len(responses) == 0
                    else responses[0]["created_at"],
                    "metadata": None,
                },
            )
        except DuplicateKeyError:
            continue
    print("Prompts created...")

    # Migrate responses in sql_questions and nl_questions collections
    responses = storage.find_all("responses")
    for response in responses:
        # create sql_generation
        try:
            storage.insert_one(
                "sql_generations",
                {
                    "_id": response["_id"],
                    "prompt_id": str(response["question_id"]),
                    "evaluate": False if response["confidence_score"] is None else True,
                    "sql": response["sql_query"],
                    "status": "VALID"
                    if response["sql_generation_status"] == "VALID"
                    else "INVALID",
                    "completed_at": response["created_at"]
                    + timedelta(seconds=response["exec_time"])
                    if response["exec_time"]
                    else None,
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
                    "sql_generation_id": response["question_id"],
                    "nl_answer": response["response"],
                    "created_at": response["created_at"]
                    + timedelta(seconds=response["exec_time"])
                    if response["exec_time"]
                    else response["created_at"],
                    "metadata": None,
                },
            )
    print("SQL_generations and NL_generations created...")
