from bson.objectid import ObjectId


# temporary fix for cases where { '$oid': '1234567890' } is either a dict or ObjectId,
# I believe it is both bson and mongo's issue
def get_object_id(id):
    if not isinstance(id, ObjectId):
        return ObjectId(id["$oid"])
    return id
