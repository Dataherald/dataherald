import os

from dotenv import load_dotenv
from pymongo import MongoClient


class MongoDbLocalClient:
    def __init__(self):
        load_dotenv()
        uri = os.getenv('MONGODB_URI_LOCAL')
        db_name = os.getenv('MONGODB_DB_NAME')

        print(f"uri: {uri}")

        self.client = MongoClient(uri)
        self.db_name = db_name
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def select(self, collection_name, query=None, projection=None):
        collection = self.db[collection_name]
        return collection.find(query, projection)

    def close(self):
        self.client.close()

    def switch_database(self, db_name):
        self.db_name = db_name
        self.db = self.client[db_name]

    def drop_collection(self, collection_name):
        print("Dropping collection: " + collection_name +
              " from database: " + self.db_name)
        self.db[collection_name].drop()

    def get_all_instructions_for_connection_id(self, db_connection_id: str):
        """Given a db_connection_id return _all_ the instructions (_id) for that connection

        Collection Name: instructions
        _id: ObjectId
        db_connection_id: str
        instruction: str

        Args:
            db_connection_id (str): the db_connection_id to get the instructions for
        """
        query = {"db_connection_id": db_connection_id}
        projection = {"_id": 1}
        result = self.select("instructions", query, projection)

        if result is None:
            return None

        # return all ids in a list
        return [str(item["_id"]) for item in result]

    def get_all_golden_records_for_connection_id(self, db_connection_id: str):
        """Given a db_connection_id return _all_ the golden records (_id) for that connection

        Collection Name: golden_records
        _id: ObjectId
        db_connection_id: str
        question: str
        sql_query: str

        Args:
            db_connection_id (str): the db_connection_id to get the golden records for
        """
        query = {"db_connection_id": db_connection_id}
        projection = {"_id": 1}
        result = self.select("golden_records", query, projection)

        if result is None:
            return None

        # return all ids in a list
        return [str(item["_id"]) for item in result]

    def get_db_connection_id_for_db_alias(self, db_alias: str) -> str:
        """Given a db_alias return the db_connection_id from the database_connections collection

        Args:
            db_alias (str): the db_alias to get the id for

        Returns:
            str: the db_connection_id or None if not found
        """

        # select the _id from the database_connections collection where alias = alias
        query = {"alias": db_alias}
        projection = {"_id": 1}
        result = self.select("database_connections", query, projection)

        # check if the result is empty
        if result is None:
            return None

        # get the first item in the list
        return str(list(result)[0]["_id"])
