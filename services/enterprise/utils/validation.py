from bson.objectid import ObjectId as BsonObjectId


class PyObjectId(BsonObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, BsonObjectId):
            raise TypeError("ObjectId required")
        return str(v)


class ObjectIdString(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return str(BsonObjectId(v))
        except Exception as e:
            raise ValueError("Invalid ObjectId") from e
