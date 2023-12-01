import csv
import sys
import uuid

import pymongo
from bson import ObjectId

import config


def create_csv_file(
    rows: list,
):
    file_location = f"{str(uuid.uuid4())}.csv"
    print(file_location)
    with open(file_location, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(row.values())


if __name__ == "__main__":
    input_list = sys.argv[1:]

    output_dict = {}

    for i in range(0, len(input_list), 2):
        key = input_list[i]
        value = input_list[i + 1]
        output_dict[key] = value

    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]

    filter = {}
    if "organization_id" in output_dict.keys():
        filter["organization_id"] = ObjectId(output_dict["organization_id"])
    if (
        "question_date_gte" in output_dict.keys()
        or "question_date_lt" in output_dict.keys()
    ):
        filter["question_date"] = {}
    if "question_date_gte" in output_dict.keys():
        filter["question_date"]["$gte"] = output_dict["question_date_gte"]
    if "question_date_lt" in output_dict.keys():
        filter["question_date"]["$lt"] = output_dict["question_date_lt"]

    queries = data_store["queries"].find(filter)

    rows = []
    for query in queries:
        question = data_store["questions"].find_one({"_id": query["question_id"]})
        responses = (
            data_store["responses"]
            .find({"question_id": query["question_id"]})
            .sort("created_at", -1)
        )
        responses = list(responses)

        if len(responses) > 0:
            original_response = responses[-1]
            final_response = responses[0]
            rows.append(
                {
                    "query_id": query["display_id"],
                    "question_id": str(query["question_id"]),
                    "question": question["question"],
                    "original_confidence": original_response["confidence_score"],
                    "original_sql_query": original_response["sql_query"],
                    "status": query["status"],
                    "final_sql_confidence": None
                    if len(responses) == 1
                    else final_response["confidence_score"],
                    "final_sql_query": None
                    if len(responses) == 1
                    else final_response["sql_query"],
                    "final_sql_status": None
                    if len(responses) == 1
                    else final_response["sql_generation_status"],
                    "was_the_original_correct": True
                    if query["status"] == "VERIFIED"
                    and (
                        len(responses) == 1
                        or (
                            len(responses) > 1
                            and original_response["sql_query"]
                            == final_response["sql_query"]
                        )
                    )
                    else False,
                    "question_asked_date": str(original_response["created_at"]),
                    "num_responses": len(responses),
                }
            )
    if len(rows) > 0:
        create_csv_file(rows)
    else:
        print("Empty result")
