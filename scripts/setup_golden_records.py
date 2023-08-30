"""

    This script is used to upload golden records to the database.

    A golden record is a record gives sample queries and their corresponding 'ideal' SQL queries.

    It takes a configuration file as input. The configuration file is a list of dictionaries.

    The format of each entry is as follows:

    {
      db_name: "db_alias_name",
      questions: [
        {
          "question": "string",
          "sql_query": "string"
        }
      ]
    }

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


def add_golden_record_list(db_alias: str, questions: list[str]):
    """ Add a list of golden records to the database
    The db_alias needs to be added to each item in the list of questions
    Args:
        db_alias (str): the db alias associated with the golden record
        questions (List[str]): a sample question
    """

    endpoint_url: str = f"{DATAHERALD_REST_API_URL}/api/v1/golden-records"

    # loop through the list of questions and add the db_alias to each question
    # list comprehension
    questions_with_db = [
        {"db_alias": db_alias, "question": question['question'], "sql_query": question['sql_query']} for question in questions
    ]

    print("Adding Golden Record: ")
    print(f"endpoint url: {endpoint_url}")
    print("db_alias: " + db_alias)
    print(json.dumps(questions_with_db, indent=4, sort_keys=True))
    r = requests.post(endpoint_url, json=questions_with_db, headers={
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
            if "db_alias" not in config:
                # print error message
                print("db_alias not found in config. Skipping entry.")
                # skip this entry
                continue

            db_alias = config["db_alias"]
            questions = config["questions"]

            add_golden_record_list(db_alias, questions)


if __name__ == "__main__":
    # read in the database configuration file but use the default if not provided
    print("################################################################################")
    print("                         Setup Golden Records")
    print("################################################################################")
    print(f"Current working directory: {os.getcwd()}")

    # default database configuration file
    default_config_file = str(os.path.join(os.path.dirname(
        __file__), "config_files", "golden_records_config.json"))

    config_file_to_use = default_config_file
    if len(sys.argv) < 2:
        print("No database configuration file provided. Using default.")
    else:
        config_file_to_use = sys.argv[1]

    run(config_file_to_use)
