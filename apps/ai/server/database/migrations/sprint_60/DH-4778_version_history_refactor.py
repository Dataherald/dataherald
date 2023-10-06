import pymongo
from bson import ObjectId

import config

# run this script after the migration script from engine
if __name__ == "__main__":
    query_collection = "queries"

    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]

    try:
        data_store["nl_query_response_refs"].rename(query_collection)
    except Exception as e:
        print(e)
        pass

    try:
        # rename query_response_id to response_id
        data_store[query_collection].update_many(
            {}, {"$rename": {"query_response_id": "response_id"}}
        )
        # rename query_response_id to query_id
        data_store["golden_sql_refs"].update_many(
            {}, {"$rename": {"query_response_id": "query_id"}}
        )

        cursor = data_store[query_collection].find({})

        for doc in cursor:
            query_response = data_store["responses"].find_one(
                {"_id": doc["response_id"]}
            )

            if query_response:
                question_id = ObjectId(query_response["question_id"])
                updated_by = ObjectId(doc["updated_by"])

                # add new field question id, change updated_by to ObjectId
                data_store[query_collection].update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"question_id": question_id, "updated_by": updated_by}},
                )

                golden_sql = data_store["golden_sql_refs"].find_one(
                    {"query_id": doc["response_id"]}
                )
                if golden_sql:
                    # update query_id to be the query id
                    data_store["golden_sql_refs"].update_one(
                        {"_id": golden_sql["_id"]},
                        {"$set": {"query_id": doc["_id"]}},
                    )

    except Exception as e:  # noqa: S110
        print(e)
        pass
