import os

import pymongo
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from sql_metadata import Parser

pinecone_api_key = os.environ.get("PINECONE_API_KEY")

pinecone_index_name = os.environ.get("PINECONE_INDEX_NAME")
mongodb_uri = os.environ.get("MONGODB_URI")
mongodb_username = os.environ.get("MONGODB_USERNAME")
mongodb_password = os.environ.get("MONGODB_PASSWORD")
mongodb_name = os.environ.get("MONGODB_NAME", "ephemeral-serverless")

openai_api_key = os.environ.get("OPENAI_API_KEY")

EMBEDDING_MODEL = "text-embedding-3-small"

if __name__ == "__main__":
    pinecone = Pinecone(api_key=pinecone_api_key)
    mongodb_uri = mongodb_uri.replace("mongodb+srv://", "")
    connection_string = (
        f"mongodb+srv://{mongodb_username}:{mongodb_password}@{mongodb_uri}"
    )
    data_store = pymongo.MongoClient(connection_string)[mongodb_name]

    golden_sqls = list(data_store["golden_sqls"].find())

    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key, model=EMBEDDING_MODEL)
    index = pinecone.Index(pinecone_index_name)
    batch_limit = 100
    count = 0
    for limit_index in range(0, len(golden_sqls), batch_limit):
        golden_sql_batch = golden_sqls[limit_index : limit_index + batch_limit]
        embeds = embedding.embed_documents(
            [record["prompt_text"] for record in golden_sql_batch]
        )
        records = []
        for key in range(len(golden_sql_batch)):
            parsed_tables = Parser(golden_sql_batch[key]["sql"]).tables
            if len(parsed_tables) > 0:
                records.append(
                    (
                        str(golden_sql_batch[key]["_id"]),
                        embeds[key],
                        {
                            "tables_used": parsed_tables[0],
                            "db_connection_id": golden_sql_batch[key][
                                "db_connection_id"
                            ],
                        },
                    )
                )
        index.upsert(vectors=records)
        count += len(records)
    print("Indexing done!")
    print(f"Indexed {count} records")
