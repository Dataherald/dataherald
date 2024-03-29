import argparse
import asyncio

import pymongo

import config


async def copy_organization_resources(args: dict):
    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]
    org_a_id = args["organization_a_id"]
    org_b_id = args["organization_b_id"]

    db_connection_dict = {}

    if args["database_connection"]:
        count = 0
        data_store["database_connections"].delete_many(
            {"metadata.dh_internal.organization_id": org_b_id}
        )
        cursor = data_store["database_connections"].find(
            {"metadata.dh_internal.organization_id": org_a_id}
        )
        for db_connection in cursor:
            old_id = str(db_connection["_id"])
            db_connection["metadata"]["dh_internal"]["organization_id"] = org_b_id
            del db_connection["_id"]
            new_db_connection_id = str(
                data_store["database_connections"].insert_one(db_connection).inserted_id
            )
            db_connection_dict[old_id] = new_db_connection_id
            count += 1
        print(f"Copy database connection: {count} document(s) copied")

    if args["table_description"]:
        count = 0
        data_store["table_descriptions"].delete_many(
            {"metadata.dh_internal.organization_id": org_b_id}
        )
        cursor = data_store["table_descriptions"].find(
            {"db_connection_id": {"$in": list(db_connection_dict.keys())}}
        )
        for table_description in cursor:
            new_table_description = format_copied_resource(
                table_description, org_b_id, db_connection_dict
            )
            data_store["table_descriptions"].insert_one(new_table_description)
            count += 1
        print(f"Copy table descriptions: {count} document(s) copied")

    if args["instructions"]:
        count = 0
        data_store["instructions"].delete_many(
            {"metadata.dh_internal.organization_id": org_b_id}
        )
        cursor = data_store["instructions"].find(
            {"db_connection_id": {"$in": list(db_connection_dict.keys())}}
        )
        for instruction in cursor:
            new_instruction = format_copied_resource(
                instruction, org_b_id, db_connection_dict
            )
            data_store["instructions"].insert_one(new_instruction)
            count += 1
        print(f"Copy instructions: {count} document(s) copied")

    if args["golden_sqls"]:
        count = 0
        data_store["golden_sqls"].delete_many(
            {"metadata.dh_internal.organization_id": org_b_id}
        )
        cursor = data_store["golden_sqls"].find(
            {"db_connection_id": {"$in": list(db_connection_dict.keys())}}
        )
        for golden_sql in cursor:
            new_golden_sql = format_copied_resource(
                golden_sql, org_b_id, db_connection_dict
            )
            data_store["golden_sqls"].insert_one(new_golden_sql)
            count += 1
        print(f"Copy {count} golden sqls")
        print("TODO: run the populate pinecone db script after")


def format_copied_resource(resource: dict, org_b_id: str, db_connection_dict: dict):
    resource["db_connection_id"] = db_connection_dict[resource["db_connection_id"]]
    resource["metadata"]["dh_internal"]["organization_id"] = org_b_id
    del resource["_id"]
    return resource


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Copy organization resources",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "organization_a_id",
        help="The organization id to copy resources from",
    )

    parser.add_argument(
        "organization_b_id",
        help="The organization id to copy resources to",
    )

    parser.add_argument(
        "-d",
        "--database-connection",
        action="store_true",
        help="Copy database connections",
    )

    parser.add_argument(
        "-td",
        "--table-description",
        action="store_true",
        help="Copy table descriptions",
    )

    parser.add_argument(
        "-i",
        "--instructions",
        action="store_true",
        help="Copy instructions",
    )

    parser.add_argument(
        "-gs",
        "--golden-sqls",
        action="store_true",
        help="Copy golden sqls, be sure to run the populate pinecone db script after",
    )

    args = vars(parser.parse_args())

    asyncio.run(copy_organization_resources(args))
