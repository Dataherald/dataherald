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
    print("updated golden_sqls")

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
    print("updated database_connections")

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
    print("updated prompts")

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
    print("updated sql_generations")

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
    print("updated nl_generations")

    # update db-connection id in organization to type string
    organization_cursor = data_store["organizations"].find({})
    for organization in organization_cursor:
        data_store["organizations"].update_one(
            {"_id": organization["_id"]},
            {"$set": {"db_connection_id": str(organization["db_connection_id"])}},
        )
    print("updated db_connection_id in organizations")

    # update organization id in user to type string
    user_cursor = data_store["users"].find({})
    for user in user_cursor:
        data_store["users"].update_one(
            {"_id": user["_id"]},
            {"$set": {"organization_id": str(user["organization_id"])}},
        )
    print("updated organization_id in users")

    # add organization id to table-descriptions
    table_description_cursor = data_store["table_descriptions"].find({})
    for table_description in table_description_cursor:
        db_connection = data_store["database_connections"].find_one(
            {"_id": ObjectId(table_description["db_connection_id"])}
        )
        if not db_connection:
            print(
                f"db_connection not found for table_description {str(table_description['_id'])}"
            )
            continue
        data_store["table_descriptions"].update_one(
            {"_id": table_description["_id"]},
            {
                "$set": {
                    "metadata": {
                        "dh_internal": {
                            "organization_id": db_connection["metadata"]["dh_internal"][
                                "organization_id"
                            ]
                        }
                    }
                }
            },
        )
    print("added organization_id to table_descriptions")

    # add organization id to instructions
    instruction_cursor = data_store["instructions"].find({})
    for instruction in instruction_cursor:
        db_connection = data_store["database_connections"].find_one(
            {"_id": ObjectId(instruction["db_connection_id"])}
        )
        if not db_connection:
            print(f"db_connection not found for instruction {str(instruction['_id'])}")
            continue
        data_store["instructions"].update_one(
            {"_id": instruction["_id"]},
            {
                "$set": {
                    "metadata": {
                        "dh_internal": {
                            "organization_id": db_connection["metadata"]["dh_internal"][
                                "organization_id"
                            ]
                        }
                    }
                }
            },
        )

    print("finished")
