from bson import ObjectId

from config import TABLE_DESCRIPTION_COL
from database.mongo import MongoDB
from modules.table_description.models.entities import TableDescription


class TableDescriptionRepository:
    def get_table_descriptions(
        self, db_connection_id: str, org_id, table_name: str = ""
    ) -> list[TableDescription]:
        query = {
            "db_connection_id": db_connection_id,
            "metadata.dh_internal.organization_id": org_id,
        }
        if table_name:
            query["table_name"] = table_name
        table_descriptions = MongoDB.find(
            TABLE_DESCRIPTION_COL,
            query,
        )

        return [
            TableDescription(id=str(table_description["_id"]), **table_description)
            for table_description in table_descriptions
        ]

    def get_table_description(
        self, table_description_id: str, org_id: str
    ) -> TableDescription:
        table_description = MongoDB.find_one(
            TABLE_DESCRIPTION_COL,
            {
                "_id": ObjectId(table_description_id),
                "metadata.dh_internal.organization_id": org_id,
            },
        )
        return (
            TableDescription(id=str(table_description["_id"]), **table_description)
            if table_description
            else None
        )

    def get_table_description_grouped_by_db_connection_id(
        self, tables_description_ids: list[str]
    ) -> list[dict]:
        ids = [ObjectId(id) for id in tables_description_ids]

        pipeline = [
            {"$match": {"_id": {"$in": ids}}},  # Filter documents by _id
            {
                "$group": {
                    "_id": "$db_connection_id",
                    "count": {"$sum": 1},
                    "documents": {"$push": "$$ROOT"},
                }
            },
        ]

        return list(MongoDB.aggregate(TABLE_DESCRIPTION_COL, pipeline))
