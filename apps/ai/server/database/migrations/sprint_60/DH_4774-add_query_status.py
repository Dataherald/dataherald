import config
from database.mongo import MongoDB

if __name__ == "__main__":
    # Update add status
    query_refs = MongoDB.find(config.QUERY_RESPONSE_REF_COL, {})

    for query_ref in query_refs:
        if "status" not in query_ref:
            query_response = MongoDB.find_one(
                config.QUERY_RESPONSE_COL,
                {"_id": query_ref["query_response_id"]},
            )
            golden_sql = MongoDB.find_one(
                config.GOLDEN_SQL_REF_COL,
                {"query_response_id": query_ref["query_response_id"]},
            )

            if query_response["sql_generation_status"] == "VALID" and golden_sql:
                query_ref["status"] = "VERIFIED"
            elif query_response["sql_generation_status"] == "VALID":
                query_ref["status"] = "NOT_VERIFIED"
            else:
                query_ref["status"] = "SQL_ERROR"

            # update object
            MongoDB.update_one(
                config.QUERY_RESPONSE_REF_COL,
                {"_id": query_ref["_id"]},
                query_ref,
            )
