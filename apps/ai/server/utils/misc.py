from bson.objectid import ObjectId

from database.mongo import DESCENDING, MongoDB

MAX_DISPLAY_ID = 99999


# temporary fix for cases where { '$oid': '1234567890' } is either a dict or ObjectId,
# I believe it is both bson and mongo's issue
def get_object_id(id):
    if not isinstance(id, ObjectId):
        return ObjectId(id["$oid"])
    return id


def get_next_display_id(collection, org_id: ObjectId, prefix: str) -> str:
    last_query_ref_result = list(
        MongoDB.find(
            collection,
            {"organization_id": org_id, "display_id": {"$exists": True}},
        )
        .sort("display_id", DESCENDING)
        .limit(1)
    )

    if len(last_query_ref_result) > 0:
        last_display_id: str = last_query_ref_result[0]["display_id"]
        last_display_id_num = int(last_display_id.split("-")[-1])

        if last_display_id_num > MAX_DISPLAY_ID:
            next_disaply_id_num = 0
        else:
            next_disaply_id_num = last_display_id_num + 1

        return f"{prefix}-{next_disaply_id_num:05d}"

    return f"{prefix}-00000"
