"""

    This script is used to scan all the relevent tables in the set up databases and also add meta data.

    The format of each entry is as follows:

    {
      db_name: "alias_name",
      table_name: "table_name",
      table_description: "string",
      table_columns: [
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

# constants. TODO: move to a config file
DATAHERALD_REST_API_URL = "http://localhost"

DB_CONNECTION_ID = "650abe8e9baa67d0f0f47247"


def scan_table(alias: str, table_name: str):
    """scan the given table in the given database
    Args:
        alias (str): the db alias to scan
        table_name (str): the table name to scan
    """

    scanner_endpoint_url: str = f"{DATAHERALD_REST_API_URL}/api/v1/table-descriptions/scan"
    scanner_request_body: dict = {
        "db_connection_id": DB_CONNECTION_ID,
        "table_names": [table_name]
    }

    print("scanner request: ")
    print(f"endpoint url: {scanner_endpoint_url}")
    print("alias: " + alias)
    print("table_name: " + table_name)
    print(json.dumps(scanner_request_body, indent=4, sort_keys=True))
    r = requests.post(scanner_endpoint_url, json=scanner_request_body, headers={
        "Content-Type": "application/json", "Accept": "application/json"}, timeout=300)
    print(r.status_code)
    print(r.text)
    print()


def add_table_meta_data(alias: str, table_name: str, table_description: str, table_columns: list):
    """This function adds meta data to the given table in the given database

    Args:
        alias (str): the db alias
        table_name (str): the table name
        table_description (str): Meta data description of the table
        table_columns (list): Meta data for each column in the table
    """
    # construct the REST API call
    # construct the URL
    endpoint_url: str = f"{DATAHERALD_REST_API_URL}/api/v1/scanned-db/{DB_CONNECTION_ID}"

    # construct the request body
    request_body: dict = {
        "table_description": table_description,
        "table_columns": table_columns
    }

    # 3. Run the REST API call to create the database in Dataherald
    # set accept header to application/json
    print("Meta Data Add Request: ")
    print(f"endpoint url: {endpoint_url}")
    print("alias: " + alias)
    print("table_name: " + table_name)
    print("table_description: " + table_description)
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
            table_description = config["table_description"]
            table_columns = config["table_columns"]

            # first execute the scanner to add the table to the database
            # construct the URL
            # scan_table(alias, table_name)

            # second add meta data to the table
            add_table_meta_data(alias, table_name,
                                table_description, table_columns)


if __name__ == "__main__":
    print("################################################################################")
    print("                      Running setup_scanner.py")
    print("################################################################################")
    # read in the database configuration file but use the default if not provided
    print(f"Current working directory: {os.getcwd()}")

    # default database configuration file
    default_config_file = str(os.path.join(os.path.dirname(
        __file__), "config_files", "scanner_config.json"))

    config_file_to_use = default_config_file
    if len(sys.argv) < 2:
        print("No database configuration file provided. Using default.")
    else:
        config_file_to_use = sys.argv[1]

    run(config_file_to_use)
