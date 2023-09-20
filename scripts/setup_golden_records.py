"""

    This script is used to upload golden records to the database.

    A golden record is a record gives sample queries and their corresponding 'ideal' SQL queries.
    
    Golden records are retreived from the Database

    It takes a configuration file as input. The configuration file is a list of dictionaries.

    The database has the following columns
    select id, DbsReferenced, Labels, Question, SqlQuery, luser, lupdate from darwin.marvin_config_queries;
    
    The db_alias will default to 'hkg02p'

    1. Query the database for the list of golden records
    2. Loop through the database configuration file and construct the REST API call
    3. Run the REST API call to create the database in Dataherald

  """

import json
import os
import sys

import requests
from rh_python_common import db

# constants. TODO: move to a config file
DATAHERALD_REST_API_URL = "http://localhost"

endpoint_url: str = f"{DATAHERALD_REST_API_URL}/api/v1/golden-records"


def add_golden_record_list(db_alias: str, questions: list[str]):
    """ Add a list of golden records to the database
    The db_alias needs to be added to each item in the list of questions
    Args:
        db_alias (str): the db alias associated with the golden record
        questions (List[str]): a sample question
    """

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


def add_golden_record(db_alias: str, question: str, sql_query: str):
    """Add a single golden record to the database
    The db_alias needs to be added to each item in the list of questions

    Args:
        db_alias (str): the db alias associated with the golden record
        question (str): the question
        sql_query (str): the corresponding sql query
    """

    print("Adding Golden Record: ")
    print(f"db_alias: {db_alias}")
    print(f"question: {question}")
    print(f"sql_query: {sql_query}")
    print(f"endpoint url: {endpoint_url}")

    question_with_db = {"db_alias": db_alias,
                        "question": question, "sql_query": sql_query}

    r = requests.post(endpoint_url, json=question_with_db, headers={
                      "Content-Type": "application/json", "Accept": "application/json"}, timeout=300)
    print(r.status_code)
    print(r.text)
    print()


def run():
    # 1. Query the database for the list of golden records
    qry = f"""
      select Question, SqlQuery from darwin.marvin_config_queries;
    """
    questions_df = db.query_hkg02p(qry)

    # 2. Loop through the database configuration file and construct the REST API call
    for index, row in questions_df.iterrows():
        print(f"index: {index}")
        print(f"row: {row}")
        print(f"row['Question']: {row['Question']}")
        print(f"row['SqlQuery']: {row['SqlQuery']}")
        db_alias = "hkg02p"
        question = row["questions"]
        sql = row['SqlQuery']

        add_golden_record(db_alias, question, sql)


if __name__ == "__main__":
    # read in the database configuration file but use the default if not provided
    print("################################################################################")
    print("                         Setup Golden Records")
    print("################################################################################")
    print(f"Current working directory: {os.getcwd()}")

    run()
