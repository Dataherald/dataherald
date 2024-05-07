from database.mongo import DESCENDING, MongoDB
from exceptions.exceptions import ReservedMetadataKeyError

MAX_DISPLAY_ID = 99999
RESERVED_KEY = "dh_internal"


def get_next_display_id(collection, org_id: str, prefix: str) -> str:
    latest_item = MongoDB.find_one(
        collection,
        {
            "metadata.dh_internal.organization_id": org_id,
            "metadata.dh_internal.display_id": {"$exists": True},
        },
        sort=[("metadata.dh_internal.display_id", DESCENDING)],
    )
    if latest_item:
        last_display_id: str = latest_item["metadata"]["dh_internal"]["display_id"]
        last_display_id_num = int(last_display_id.split("-")[-1])

        if last_display_id_num > MAX_DISPLAY_ID:
            next_disaply_id_num = 0
        else:
            next_disaply_id_num = last_display_id_num + 1

        return f"{prefix}-{next_disaply_id_num:05d}"

    return f"{prefix}-00000"


def reserved_key_in_metadata(metadata: dict):
    if RESERVED_KEY in metadata:
        raise ReservedMetadataKeyError()
