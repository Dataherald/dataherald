import os

from bson.objectid import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient


class MongoDbLocalClient:
    def __init__(self):
        load_dotenv()
        # print all the environment variables
        print("Environment variables:")
        print(os.environ)

        uri = 'mongodb://admin:admin@mongodb:27017'
        db_name = os.getenv('MONGODB_DB_NAME')

        print(f"uri: {uri}")
        print(f"db_name: {db_name}")

        self.client = MongoClient(uri)
        self.db_name = db_name
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def select(self, collection_name, query=None, projection=None):
        collection = self.db[collection_name]
        return collection.find(query, projection)

    def select_one(self, collection_name, query=None, projection=None):
        collection = self.db[collection_name]
        return collection.find_one(query, projection)

    def close(self):
        self.client.close()

    def switch_database(self, db_name):
        self.db_name = db_name
        self.db = self.client[db_name]

    def drop_collection(self, collection_name):
        print("Dropping collection: " + collection_name +
              " from database: " + self.db_name)
        self.db[collection_name].drop()

    def get_all_instructions_for_connection_id(self, db_connection_id: str) -> list[str]:
        """Given a db_connection_id return _all_ the instructions (_id) for that connection

        Collection Name: instructions
        _id: ObjectId
        db_connection_id: str
        instruction: str

        Args:
            db_connection_id (str): the db_connection_id to get the instructions for
        """
        query = {"db_connection_id": ObjectId(db_connection_id)}
        projection = {"_id": 1}
        result = self.select("instructions", query, projection)

        results_list: list = list(result)

        if len(results_list) == 0:
            return []

        # return all ids in a list
        return [str(item["_id"]) for item in results_list]

    def get_all_golden_records_for_connection_id(self, db_connection_id: str) -> list[str]:
        """Given a db_connection_id return _all_ the golden records (_id) for that connection

        Collection Name: golden_records
        _id: ObjectId
        db_connection_id: str
        question: str
        sql_query: str

        Args:
            db_connection_id (str): the db_connection_id to get the golden records for
        """
        query = {"db_connection_id": ObjectId(db_connection_id)}
        projection = {"_id": 1}
        result = self.select("golden_records", query, projection)

        results_list: list = list(result)

        if len(results_list) == 0:
            return []

        # return all ids in a list
        return [str(item["_id"]) for item in results_list]

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

        results_list: list = list(result)

        # check if the result is empty
        if len(results_list) == 0:
            return None

        # get the first item in the list
        return str(results_list[0]["_id"])

    def check_table_is_synced(self, db_connection_id, table_name) -> bool:
        """Check if a table is synced in the MongoDB
        The collection name is table_descriptions
        The column to check is status where table_name = table_name

        Args:
            db_connection_id (str): the db_connection_id to get the table descriptions for
            table_name (str): the table name to check if it is synced

        Returns:
            bool: True if the table is synced, False otherwise
        """

        # set up the query
        query = {"db_connection_id": ObjectId(db_connection_id),
                 "table_name": table_name}
        projection = {"status": 1}
        result = self.select("table_descriptions", query, projection)

        # print the result
        results_list: list = list(result)
        print(
            f"        result from checking table {table_name} sync'd: {results_list}. Length: {len(results_list)}")

        # check the status
        if result is None:
            return False
        if len(results_list) == 0:
            return False
        if results_list[0]["status"] == "SYNCHRONIZED":
            return True

        return False
