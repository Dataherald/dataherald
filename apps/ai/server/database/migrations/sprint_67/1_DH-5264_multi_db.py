import pymongo

import config

if __name__ == "__main__":
    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]

    org_cursor = data_store["organizations"].find({})
    for org in org_cursor:
        data_store["organizations"].update_one(
            {"_id": org["_id"]},
            {
                "$set": {
                    "slack_config": {
                        "slack_installation": org["slack_installation"]
                        if "slack_installation" in org
                        else None,
                        "db_connection_id": org["db_connection_id"]
                        if "db_connection_id" in org
                        else None,
                    }
                }
            },
        )
        print("updated organization: ", str(org["_id"]))
