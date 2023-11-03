import pymongo

import config

if __name__ == "__main__":
    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]

    try:
        data_store["queries"].update_many(
            {},
            {
                "$rename": {
                    "custom_response": "message",
                    "response_id": "answer_id",
                }
            },
        )
    except Exception as e:
        print(e)
