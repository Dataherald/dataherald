import pymongo

import config

if __name__ == "__main__":
    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]

    org_cursor = data_store["organizations"].find({})

    for org in org_cursor:
        if "llm_api_key" in org:
            data_store["organizations"].update_one(
                {"_id": org["_id"]},
                {"$set": {"llm_api_key": org["llm_api_key"]["api_key"]}},
            )

    data_store["organizations"].update_many({}, {"$unset": {"llm_credentials": ""}})
