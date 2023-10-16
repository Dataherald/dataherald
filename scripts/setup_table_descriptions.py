"""

    This script is used to scan all the relevent tables in the set up databases and also add meta data.

    The format of each entry is as follows:

    /api/v1/table-descriptions/scan
    {
      db_connection_id: "string",
      table_name: ["string"],
    }
    
    /api/v1/table-descriptions/{table_description_id}
    {
      description: "string",
      columns: [
        {
          "name": "string",
          "description": "string"
        }
      ]
    }

    There can be a list of tables in each database. The script will loop through each table and add the meta data.

    1. Read in the database configuration file
    2. Loop through the database configuration file and construct the REST API call
    3. Run the REST API call to create the database in Dataherald

  """

import json
import os
import sys

import requests

from MongoDB import MongoDB

# constants. TODO: move to a config file
DATAHERALD_REST_API_URL = "http://localhost"


def register_table_description(db_connection_id: str, table_name: str):
  """scan the given table in the given database
  Args:
      alias (str): the db alias to scan
      table_name (str): the table name to scan
  """

  register_table_desc_url: str = f"{DATAHERALD_REST_API_URL}/api/v1/table-descriptions/sync-schemas"
  scanner_request_body: dict = {
      "db_connection_id": db_connection_id,
      "table_names": [table_name]
  }

  print("Table descriptions: ")
  print("====================================================")
  print(f"endpoint url: {register_table_desc_url}")
  print("db_connection_id: " + db_connection_id)
  print("table_names: [" + table_name + "]")
  print(json.dumps(scanner_request_body, indent=4, sort_keys=True))
  r = requests.post(register_table_desc_url, json=scanner_request_body, headers={
      "Content-Type": "application/json", "Accept": "application/json"}, timeout=300)
  print(r.status_code)
  print(r.text)
  print()


def add_table_meta_data(db_connection_id: str, table_description_id: str, description: str, columns: list):
  """This function adds meta data to the given table in the given database

  Args:
      alias (str): the db alias
      table_name (str): the table name
      description (str): Meta data description of the table
      columns (list): Meta data for each column in the table
  """
  # construct the REST API call
  # construct the URL
  endpoint_url: str = f"{DATAHERALD_REST_API_URL}/api/v1/table-descriptions/{table_description_id}"

  # construct the request body
  request_body: dict = {
      "description": description,
      "columns": columns
  }

  # 3. Run the REST API call to create the database in Dataherald
  # set accept header to application/json
  print("Meta Data Add Request: ")
  print(f"endpoint url: {endpoint_url}")
  print("db_connection_id: " + db_connection_id)
  print("table_description_id : " + table_description_id)
  print("table_description: " + description)
  print("request body: ")
  print(json.dumps(request_body, indent=4, sort_keys=True))
  # print the endpoint url
  print(f"endpoint url: {endpoint_url}")
  r = requests.patch(endpoint_url, data=json.dumps(request_body), headers={
      "Content-Type": "application/json", "Accept": "application/json"}, timeout=300)
  print(r.status_code)
  print(r.text)
  print()


def run(config_file: str):
  # 1. Read in the database configuration file
  with open(config_file) as f:
    data = json.load(f)

    # 2. Loop through the database configuration file and construct the REST API call
    # get next item in the list
    for config in data:
      # print the config
      print(json.dumps(config, indent=4, sort_keys=True))
      if "alias" not in config:
        # print error message
        print("alias not found in config. Skipping entry.")
        # skip this entry
        continue

      alias = config["alias"]
      table_name = config["table_name"]
      description = config["description"]
      columns = config["columns"]

      # first execute the scanner to add the table to the database
      # construct the URL

      # get the db_connection_id from the mongo database /
      mongo = MongoDB()
      db_connection_id = mongo.get_db_connection_id_for_db_alias(
          alias)
      mongo.close()

      if db_connection_id is None:
        print(f"db_connection_id not found for db: {alias}")
        continue

      print(f"db_connection_id: {db_connection_id}")

      register_table_description(db_connection_id, table_name)

      # get the _id from the table_descriptions collection where db_connection_id = db_connection_id and table_name = table_name

      mongo = MongoDB()
      table_description_id = mongo.get_table_desc_id_for_dblias_tablename(
          db_connection_id, table_name)
      mongo.close()

      if table_description_id is None:
        print(
            f"table_description_id not found for db: {alias} and table: {table_name}")
        continue

      # second add meta data to the table
      add_table_meta_data(db_connection_id,
                          table_description_id, description, columns)


if __name__ == "__main__":
  print("################################################################################")
  print("                      Running setup_table_descriptions.py")
  print("################################################################################")
  # read in the database configuration file but use the default if not provided
  print(f"Current working directory: {os.getcwd()}")

  # default database configuration file
  default_config_file = str(os.path.join(os.path.dirname(
      __file__), "config_files", "table_descriptions.json"))

  config_file_to_use = default_config_file
  if len(sys.argv) < 2:
    print("No database configuration file provided. Using default.")
  else:
    config_file_to_use = sys.argv[1]

  run(config_file_to_use)
