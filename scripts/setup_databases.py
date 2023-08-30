"""
read in the database configuration file in json format and then run a REST API call to create the database in Dataherald
the database configuration file is in the format of:

Without a SSH connection
{
  "db_alias": "test_db",
  "use_ssh": false,
  "connection_uri": "sqlite:///mydb.db"
}

With a SSH connection
{
  "db_alias": "my_db_alias_identifier",
  "use_ssh": true,
  "ssh_settings": {
    "db_name": "db_name",
    "host": "string",
    "username": "string",
    "password": "string",
    "remote_host": "string",
    "remote_db_name": "string",
    "remote_db_password": "string",
    "private_key_path": "string",
    "private_key_password": "string",
    "db_driver": "string"
  }
}
"""

# 1. Read in the database configuration file
# 2. Loop through the database configuration file and construct the REST API call
# 3. Run the REST API call to create the database in Dataherald

import json
import os
import sys

import requests

# constants. TODO: move to a config file
DATAHERALD_REST_API_URL = "http://localhost"
DATAHERALD_REST_CREATE_DATABASE_END_POINT = "/api/v1/database"


def main():
    # 1. Read in the database configuration file
    with open(sys.argv[1]) as f:
        data = json.load(f)

    # log the database configuration file
    print(f"Database configuration file: {sys.argv[1]}")
    print(json.dumps(data, indent=4, sort_keys=True))

    # 2. Loop through the database configuration file and construct the REST API call
    request_body = {}
    for db in data:
        # construct the REST API call
        if db["use_ssh"]:
            print("Creating database {} with SSH connection".format(
                db["db_alias"]))
            request_body: dict = {
                "db_alias": db["db_alias"],
                "use_ssh": db["use_ssh"],
                "ssh_settings": db["ssh_settings"],
                "connection_uri": db["connection_uri"],
            }
        else:
            print("Creating database {} without SSH connection".format(
                db["db_alias"]))
            request_body: dict = {
                "db_alias": db["db_alias"],
                "use_ssh": db["use_ssh"],
                "connection_uri": db["connection_uri"],
            }

        # 3. Run the REST API call to create the database in Dataherald
        # set accept header to application/json
        if "db_alias" in request_body:
            # print the request body
            print("request body: ")
            print(json.dumps(request_body, indent=4, sort_keys=True))
            endpoint_url: str = f"{DATAHERALD_REST_API_URL}{DATAHERALD_REST_CREATE_DATABASE_END_POINT}"
            # print the endpoint url
            print(f"endpoint url: {endpoint_url}")
            r = requests.post(endpoint_url, json=request_body, headers={
                              "Content-Type": "application/json", "Accept": "application/json"}, timeout=10)
            print(r.status_code)
            print(r.text)
            print()
        else:
            # print error message
            print("Error: Not a correctly formatted database request")


if __name__ == "__main__":
    print("################################################################################")
    print("                         Setup Databases")
    print("################################################################################")
    # read from the command line otherwise use the default
    # print the current working directory
    print(f"Current working directory: {os.getcwd()}")
    default_db_config_file = os.path.join(
        "scripts", "config_files", "db_config.json")
    min_args = 2
    if len(sys.argv) < min_args:
        sys.argv.append(default_db_config_file)

    main()
