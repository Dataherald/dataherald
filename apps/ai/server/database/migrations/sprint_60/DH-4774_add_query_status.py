import pymongo

import config

if __name__ == "__main__":
    # Update add status
    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]

    query_refs = data_store["nl_query_response_refs"].find({})
    for query_ref in query_refs:
        if "status" not in query_ref:
            query_response = data_store["nl_query_responses"].find_one(
                {"_id": query_ref["query_response_id"]},
            )
            golden_sql = data_store["golden_sql_refs"].find_one(
                {"query_response_id": query_ref["query_response_id"]},
            )

            if query_response["sql_generation_status"] == "VALID" and golden_sql:
                query_ref["status"] = "VERIFIED"
            elif query_response["sql_generation_status"] == "VALID":
                query_ref["status"] = "NOT_VERIFIED"
            else:
                query_ref["status"] = "SQL_ERROR"

            # update object
            data_store["nl_query_response_refs"].update_one(
                {"_id": query_ref["_id"]}, {"$set": query_ref}
            )
