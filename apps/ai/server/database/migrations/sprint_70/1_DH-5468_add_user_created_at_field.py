import pymongo

import config


def get_creation_time_from_objectid(objectid):
    """Extract creation datetime from ObjectId."""
    return objectid.generation_time


if __name__ == "__main__":
    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]

    # Query to find users without a created_at field
    users_without_created_at = data_store["users"].find(
        {"created_at": {"$exists": False}}
    )

    updated_count = 0  # Initialize updated users count

    # Update each user individually to avoid overriding existing fields
    for user in users_without_created_at:
        creation_time = get_creation_time_from_objectid(user["_id"])
        # Update user document with created_at field
        result = data_store["users"].update_one(
            {"_id": user["_id"]}, {"$set": {"created_at": creation_time}}
        )

        # Increment count if a document was updated
        if result.modified_count > 0:
            updated_count += 1

    print(f"Added 'created_at' field to {updated_count} users without it.")
