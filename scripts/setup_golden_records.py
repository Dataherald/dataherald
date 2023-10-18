"""

    This script is used to upload golden records to the database.

    A golden record is a record gives sample queries and their corresponding 'ideal' SQL queries.

    Golden records are retreived from the Database

    The database has the following columns
    select id, DbsReferenced, Labels, Question, SqlQuery, luser, lupdate from darwin.marvin_config_queries;

    The db_alias will default to 'hkg02p'

    1. Query the database for the list of golden records
    2. Loop through the database configuration file and construct the REST API call
    3. Run the REST API call to create the database in Dataherald

  """

import json
import os

import requests
from mongodb import MongoDbLocalClient
from rh_python_common import db

# constants. TODO: move to a config file
DATAHERALD_REST_API_URL = "http://localhost"

endpoint_url: str = f"{DATAHERALD_REST_API_URL}/api/v1/golden-records"


def escape_quotes(s: str) -> str:
    return s.replace("'", "''")


def add_golden_record(payload: list):
    """Add a single golden record to the database
    The db_alias needs to be added to each item in the list of questions

    Args:
        db_connection_id (str): the db_connection_id to apply golden record to
        question (str): the question
        sql_query (str): the corresponding sql query
    """

    # print the payload
    print("payload: ")
    print(json.dumps(payload, indent=4, sort_keys=True))

    r = requests.post(endpoint_url, json=payload, headers={
                      "Content-Type": "application/json", "Accept": "application/json"}, timeout=300)
    print(r.status_code)
    print(r.text)

    print()


def delete_golden_record_with_id(golden_record_id: str):
    """Delete a single golden record from the database

    Args:
        golden_record_id (str): the golden record id to delete
    """

    # print the payload
    print(f"Deleting golden record with id: {golden_record_id}")

    r = requests.delete(f"{endpoint_url}/{golden_record_id}", headers={
        "Content-Type": "application/json", "Accept": "application/json"}, timeout=300)
    print(r.status_code)
    print(r.text)

    print()


def delete_all_existing_golden_record():
    """
    1. Query the mongodb database for the list of Golden Records
    2. Loop through the database configuration file and construct the REST API call to delete the Golden Records
    3. Run the REST API call to delete the golden record in Dataherald
    """

    # 1. Query the mongodb database for the list of golden records
    db_alias = "hkg02p"
    mongo = MongoDbLocalClient()
    db_id = mongo.get_db_connection_id_for_db_alias(db_alias)
    golden_records = mongo.get_all_golden_records_for_connection_id(db_id)
    mongo.close()

    # 2. Loop through the database configuration file and construct the REST API call to delete the golden records
    for golden_record in golden_records:
        print(f"Deleting golden record: {golden_record}")
        delete_golden_record_with_id(golden_record)


def run():
    # 0. Pre delete all existing golden records
    delete_all_existing_golden_record()

    # 1. Query the database for the list of golden records
    qry = """
      select Question, SqlQuery from darwin.marvin_config_queries;
    """
    questions_df = db.query_hkg02p(qry)

    # 2. Loop through the database configuration file and construct the REST API call
    api_payload = []
    for index, row in questions_df.iterrows():
        print(f"index: {index}")
        print(f"row: {row}")
        print(f"row['Question']: {row['Question']}")
        print(f"row['SqlQuery']: {row['SqlQuery']}")
        db_alias = "hkg02p"

        # get the db_connection_id from the mongo database /
        mongo = MongoDbLocalClient()
        db_id = mongo.get_db_connection_id_for_db_alias(db_alias)
        mongo.close()

        if db_id is None:
            print(f"db_alias: {db_alias} not found in database_connections")
            continue

        question = row["Question"]
        sql = row['SqlQuery']

        api_payload.append(
            {"db_connection_id": db_id, "question": question, "sql_query": sql})

    if len(api_payload) == 0:
        print("No golden records found in database")
        return
    add_golden_record(api_payload)


if __name__ == "__main__":
    # read in the database configuration file but use the default if not provided
    print("################################################################################")
    print("                         Setup Golden Records")
    print("################################################################################")
    print(f"Current working directory: {os.getcwd()}")

    run()
