from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os


class MongoDB:
    def __init__(self):
        load_dotenv()
        uri = os.getenv('MONGODB_URI_LOCAL')
        db_username = os.getenv('MONGODB_DB_USERNAME')
        db_password = os.getenv('MONGODB_DB_PASSWORD')
        db_name = os.getenv('MONGODB_DB_NAME')
        # if uri and db_username and db_password:
        #     uri = uri.replace(
        #         '://', f'://{quote_plus(db_username)}:{quote_plus(db_password)}@')

        print(f"uri: {uri}")

        self.client = MongoClient(uri)
        self.db_name = db_name
        self.db = self.client[db_name]

    def select(self, collection_name, query=None, projection=None):
        collection = self.db[collection_name]
        return collection.find(query, projection)

    def close(self):
        self.client.close()

    def switch_database(self, db_name):
        self.db_name = db_name
        self.db = self.client[db_name]
