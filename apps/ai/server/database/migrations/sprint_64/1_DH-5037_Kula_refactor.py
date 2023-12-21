from datetime import datetime

import pymongo
from bson import ObjectId

import config
from modules.user.service import UserService

if __name__ == "__main__":
    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]
    user_service = UserService()

    date_format = "%Y-%m-%d %H:%M:%S"

    # update golden_sql collection and add metadata field
    golden_sql_ref_cursor = data_store["golden_sql_refs"].find({})
    for golden_sql_ref in golden_sql_ref_cursor:
        data_store["golden_sqls"].update_one(
            {"_id": golden_sql_ref["golden_sql_id"]},
            {
                "$set": {
                    "metadata": {
                        "dh_internal": {
                            "source": golden_sql_ref["source"],
                            "display_id": golden_sql_ref["display_id"],
                            "organization_id": str(golden_sql_ref["organization_id"]),
                        }
                    },
                    "created_at": datetime.strptime(
                        golden_sql_ref["created_time"], date_format
                    ),
                }
            },
        )

        if "query_id" in golden_sql_ref:
            query = data_store["queries"].find_one({"_id": golden_sql_ref["query_id"]})
            data_store["golden_sqls"].update_one(
                {"_id": golden_sql_ref["golden_sql_id"]},
                {
                    "$set": {
                        "metadata.dh_internal.prompt_id": str(query["question_id"]),
                    }
                },
            )

    # update db_connection collection and add metadata field
    db_connection_ref_cursor = data_store["database_connection_refs"].find({})
    for db_connection_ref in db_connection_ref_cursor:
        data_store["database_connections"].update_one(
            {"_id": db_connection_ref["db_connection_id"]},
            {
                "$set": {
                    "metadata": {
                        "dh_internal": {
                            "organization_id": str(db_connection_ref["organization_id"])
                        },
                    }
                }
            },
        )

    # update question collection and add metadata field
    question_ref_cursor = data_store["queries"].find({})
    for question_ref in question_ref_cursor:
        user = (
            user_service.get_user(
                str(question_ref["updated_by"]), str(question_ref["organization_id"])
            )
            if question_ref["updated_by"]
            else None
        )

        created_by = (
            question_ref["slack_info"]["username"]
            if "slack_info" in question_ref
            else None
        )
        updated_by = user.name if user else None

        data_store["prompts"].update_one(
            {"_id": question_ref["question_id"]},
            {
                "$set": {
                    "metadata": {
                        "dh_internal": {
                            "organization_id": str(question_ref["organization_id"]),
                            "display_id": question_ref["display_id"],
                            "generation_status": "ERROR"
                            if question_ref["status"] == "SQL_ERROR"
                            else question_ref["status"],
                            "slack_info": question_ref["slack_info"],
                            "message": question_ref["message"]
                            if "message" in question_ref
                            else None,
                            "created_by": created_by,
                            "updated_by": updated_by,
                        }
                    },
                    "created_at": datetime.strptime(
                        question_ref["question_date"], date_format
                    ),
                }
            },
        )

    # update sql_generation and nl_generation collection metadata field
    sql_generation_cursor = data_store["sql_generations"].find({})
    for sql_generation in sql_generation_cursor:
        prompt = data_store["prompts"].find_one(
            {"_id": ObjectId(sql_generation["prompt_id"])}
        )
        data_store["sql_generations"].update_one(
            {"_id": sql_generation["_id"]},
            {
                "$set": {
                    "metadata": {
                        "dh_internal": {
                            "organization_id": prompt["metadata"]["dh_internal"][
                                "organization_id"
                            ],
                        }
                    },
                }
            },
        )

    nl_generation_cursor = data_store["nl_generations"].find({})
    for nl_generation in nl_generation_cursor:
        sql_generation = data_store["sql_generations"].find_one(
            {"_id": ObjectId(nl_generation["sql_generation_id"])}
        )
        data_store["nl_generations"].update_one(
            {"_id": nl_generation["_id"]},
            {
                "$set": {
                    "metadata": {
                        "dh_internal": {
                            "organization_id": sql_generation["metadata"][
                                "dh_internal"
                            ]["organization_id"],
                        }
                    },
                }
            },
        )

    # update ids to type string
    organization_cursor = data_store["organizations"].find({})
    for organization in organization_cursor:
        data_store["organizations"].update_one(
            {"_id": organization["_id"]},
            {"$set": {"db_connection_id": str(organization["db_connection_id"])}},
        )

    user_cursor = data_store["users"].find({})
    for user in user_cursor:
        data_store["users"].update_one(
            {"_id": user["_id"]},
            {"$set": {"organization_id": str(user["organization_id"])}},
        )
    print("finished")
