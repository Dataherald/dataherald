import pymongo

import config

if __name__ == "__main__":
    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]

    data_store["organizations"].update_many(
        {"invoice_details": {"$exists": False}},
        {"$set": {"invoice_details": {"plan": "ENTERPRISE"}}},
    )
    print("Updated all organizations to Enterprise plan.")
