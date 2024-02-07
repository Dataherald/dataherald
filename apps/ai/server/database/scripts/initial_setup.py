import json
from datetime import datetime

import pymongo
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError

import config
from modules.key.models.requests import KeyGenerationRequest
from modules.key.service import KeyService
from utils.encrypt import FernetEncrypt


def insert_or_update(data_store, collection: str, document: dict) -> str:
    id = ObjectId(document["_id"])
    try:
        document["_id"] = id
        data_store[collection].insert_one(document)
    except DuplicateKeyError:
        document.pop("_id", None)
        data_store[collection].update_one({"_id": ObjectId(id)}, {"$set": document})
    return str(id)


if __name__ == "__main__":
    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]

    fernet_encrypt = FernetEncrypt()
    db_connection_id = ObjectId("65847ee5c2f29b08592c2401")
    organization_id = ObjectId("65847ee5c2f29b08592c2402")
    finetuning_id = ObjectId("659c57d1d648d1d3a6d96373")
    api_key = "dh-016e428d9f0c1c42458fcf4f5b407584a777b2fbf8d453670c2b8fc877511035"

    insert_or_update(
        data_store,
        "database_connections",
        {
            "_id": db_connection_id,
            "alias": "snowflake_local_test",
            "use_ssh": False,
            "connection_uri": fernet_encrypt.encrypt(
                "snowflake://Leo:Dat31642099.00@ksxgmup-qrb65970/v2_real_estate/public"
            ),
            "ssh_settings": None,
            "created_at": datetime.now(),
            "metadata": {"dh_internal": {"organization_id": str(organization_id)}},
        },
    )

    print(f"DB connection: {db_connection_id}")

    insert_or_update(
        data_store,
        "organizations",
        {
            "_id": organization_id,
            "name": "Local Test",
            "confidence_threshold": 1,
            "db_connection_id": str(db_connection_id),
            "invoice_details": {
                "plan": "ENTERPRISE",
            },
        },
    )

    print(f"Organization created: {organization_id}")

    insert_or_update(
        data_store,
        "finetunings",
        {
            "_id": finetuning_id,
            "alias": "Postman test",
            "db_connection_id": str(db_connection_id),
            "status": "SUCCEEDED",
            "error": "",
            "base_llm": {
                "model_provider": "",
                "model_name": "gpt-3.5-turbo-1106",
                "model_parameters": {},
            },
            "finetuning_file_id": "file-DCovtOj6OZ54DfmYoMMyod39",
            "finetuning_job_id": "ftjob-ZyojRxCWvyki1O4v2mz4YYpn",
            "model_id": "ft:gpt-3.5-turbo-1106:dataherald::8dUNOq9W",
            "created_at": datetime.now(),
            "golden_sqls": [],
            "metadata": {"dh_internal": {"organization_id": str(organization_id)}},
        },
    )

    print(f"Finetuning created: {finetuning_id}")

    with open("database/scripts/table_descriptions.json") as jsonfile:
        table_descriptions = json.loads(jsonfile.read())
        for table_description in table_descriptions:
            table_description["created_at"] = datetime.now()
            table_description["last_schema_sync"] = datetime.now()
            table_description_id = insert_or_update(
                data_store, "table_descriptions", table_description
            )
            print(f"Table description created: {table_description_id}")

    key_service = KeyService()
    key = key_service.add_key(
        KeyGenerationRequest(name="Local Test"), str(organization_id), api_key
    )
    print(f"Key created: {key}")
