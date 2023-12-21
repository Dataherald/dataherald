from datetime import datetime

import pymongo
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError

import config
from modules.key.models.requests import KeyGenerationRequest
from modules.key.service import KeyService
from utils.encrypt import FernetEncrypt

if __name__ == "__main__":
    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]

    fernet_encrypt = FernetEncrypt()
    db_connection_id = ObjectId("65847ee5c2f29b08592c2401")
    organization_id = ObjectId("65847ee5c2f29b08592c2402")
    try:
        data_store["database_connections"].insert_one(
            {
                "_id": db_connection_id,
                "alias": "snowflake_local_test",
                "use_ssh": False,
                "uri": fernet_encrypt.encrypt(
                    "snowflake://Leo:Dat31642099.00@ksxgmup-qrb65970/v2_real_estate/public"
                ),
                "ssh_settings": None,
                "created_at": datetime.now(),
                "metadata": {"dh_internal": {"organization_id": str(organization_id)}},
            }
        )
    except DuplicateKeyError:
        pass
    print(f"DB connection: {db_connection_id}")

    try:
        data_store["organizations"].insert_one(
            {
                "_id": organization_id,
                "name": "Local Test",
                "confidence_threshold": 1,
                "db_connection_id": str(db_connection_id),
            }
        )
        print("Creates organization...")
    except DuplicateKeyError:
        pass

    key_service = KeyService()
    key = key_service.add_key(
        KeyGenerationRequest(name="Local Test"), str(organization_id)
    )
    print(f"Key created: {key}")
