import time
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
    db_connection_id = str(list(result)[0]["_id"])
    return db_connection_id

  # def get_table_desc_id_for_dblias_tablename(self, db_connection_id: str, table_name: str) -> str:
  #   """ Given a db_connection_id and table_name return the table_description_id from the table_descriptions collection

  #   Args:
  #       db_connection_id (str): the db_connection_id to get the table_description_id for
  #       table_name (str): The table_name to get the table_description_id for

  #   Returns:
  #       str: The table_description_id or None if not found
  #   """

  #   query = {"db_connection_id": db_connection_id,
  #            "table_name": table_name}
  #   projection = {"_id": 1}

  #   # try to get the result up to 3 times
  #   # sometimes the connection times out and sometimes the value is not ready
  #   # this is a hack to get around that
  #   count = 0
  #   while count < 3:
  #     time.sleep(1)
  #     result = self.select("table_descriptions", query, projection)
  #     # check if the result is empty
  #     if result is None:
  #       count += 1
  #       continue

  #     # check the number of results
  #     if len(list(result)) == 0:
  #       count += 1
  #       continue
  #     else:
  #       break

  #   if result is None:
  #     return None

  #   # get the first item in the list
  #   print("__________________________________________________________________________________________")
  #   print(f"result: {result}")
  #   print("__________________________________________________________________________________________")
  #   print(f"{list(result)}")
  #   # print the values from the pymongo.cursor.Cursor object
  #   for item in list(result):
  #     print(f"item: {item}")
  #     print(f"item['id']: {item['id']}")
  #   print("__________________________________________________________________________________________")

  #   table_description_id = str(list(result)[0]["id"])

  #   return table_description_id
