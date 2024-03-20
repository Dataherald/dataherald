import csv
import datetime
import sys
import uuid

import pymongo

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
        filter["metadata.dh_internal.organization_id"] = str(
            output_dict["organization_id"]
        )
    if (
        "question_date_gte" in output_dict.keys()
        or "question_date_lt" in output_dict.keys()
    ):
        filter["created_at"] = {}
    if "question_date_gte" in output_dict.keys():
        filter["created_at"]["$gte"] = datetime.datetime.strptime(
            output_dict["question_date_gte"], "%Y-%m-%d"
        )
    if "question_date_lt" in output_dict.keys():
        filter["created_at"]["$lt"] = datetime.datetime.strptime(
            output_dict["question_date_lt"], "%Y-%m-%d"
        )

    prompts = data_store["prompts"].find(filter)
    rows = []
    for prompt in prompts:
        sql_generations = (
            data_store["sql_generations"]
            .find({"prompt_id": str(prompt["_id"])})
            .sort("created_at", -1)
        )
        sql_generations = list(sql_generations)

        if len(sql_generations) > 0:
            original_response = sql_generations[-1]
            final_response = sql_generations[0]
            rows.append(
                {
                    "display_id": prompt["metadata"]["dh_internal"].get("display_id"),
                    "prompt_id": str(prompt["_id"]),
                    "prompt": prompt["text"],
                    "original_confidence": original_response["confidence_score"],
                    "original_sql_query": original_response["sql"],
                    "original_sql_status": original_response["status"],
                    "latest_sql_status": final_response["status"],
                    "source": prompt["metadata"]["dh_internal"].get("source"),
                    "query_status": prompt["metadata"]["dh_internal"].get(
                        "generation_status"
                    ),
                    "final_confidence": (
                        None
                        if len(sql_generations) == 1
                        else final_response["confidence_score"]
                    ),
                    "final_sql_query": (
                        None if len(sql_generations) == 1 else final_response["sql"]
                    ),
                    "final_sql_status": (
                        None if len(sql_generations) == 1 else final_response["status"]
                    ),
                    "was_the_original_correct": (
                        True
                        if (
                            prompt["metadata"]["dh_internal"]["generation_status"]
                            == "VERIFIED"
                            and (
                                len(sql_generations) == 1
                                or (
                                    len(sql_generations) > 1
                                    and original_response["sql"]
                                    == final_response["sql"]
                                )
                            )
                        )
                        or (
                            prompt["metadata"]["dh_internal"].get("source") == "SLACK"
                            and len(sql_generations) == 1
                        )
                        else False
                    ),
                    "question_asked_date": str(original_response["created_at"]),
                    "num_responses": len(sql_generations),
                }
            )
    if len(rows) > 0:
        create_csv_file(rows)
    else:
        print("Empty result")
