import json
import os
import time
import uuid
from typing import Any, List

import openai
from bson.objectid import ObjectId

from dataherald.db_scanner.models.types import TableDescription, TableDescriptionStatus
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.repositories.database_connections import DatabaseConnectionRepository
from dataherald.repositories.finetunings import FinetuningsRepository
from dataherald.repositories.golden_records import GoldenRecordRepository
from dataherald.types import Finetuning
from dataherald.utils.agent_prompts import FINETUNING_SYSTEM_INFORMATION

FILE_PROCESSING_ATTEMPTS = 20


class OpenAIFineTuning:
    finetuning_dataset_path: str

    def format_columns(self, table: TableDescription, top_k: int = 100) -> str:
        """
        format_columns formats the columns.

        Args:
            table: The table to format.
            top_k: The number of categories to show.

        Returns:
            The formatted columns in string format.
        """
        columns_information = ""
        for column in table.columns:
            name = column.name
            is_primary_key = column.is_primary_key
            if is_primary_key:
                primary_key_text = (
                    f"this column is a primary key of the table {table.table_name},"
                )
            else:
                primary_key_text = ""
            foreign_key = column.foreign_key
            if foreign_key:
                foreign_key_text = (
                    f"this column has a foreign key to the table {foreign_key},"
                )
            else:
                foreign_key_text = ""
            categories = column.categories
            if categories:
                if len(categories) <= top_k:
                    categories_text = f"Categories: {categories},"
                else:
                    categories_text = ""
            else:
                categories_text = ""
            if primary_key_text or foreign_key_text or categories_text:
                columns_information += (
                    f"{name}: {primary_key_text}{foreign_key_text}{categories_text}\n"
                )
        return columns_information

    @staticmethod
    def format_dataset(self, db_scan: List[TableDescription]) -> str:
        schema_of_database = ""
        for table in db_scan:
            tables_schema = table.table_schema
            schema_of_database += f"{tables_schema}\n"
            schema_of_database += "# Categorical Columns:\n"
            columns_information = self.format_columns(table)
            schema_of_database += columns_information
            sample_rows = table.examples
            schema_of_database += "# Sample rows:\n"
            for item in sample_rows:
                for key, value in item.items():
                    schema_of_database += f"{key}: {value}, "
                schema_of_database += "\n"
            schema_of_database += "\n\n"
        return schema_of_database

    @classmethod
    def create_fintuning_dataset(cls, fine_tuning_request: Finetuning, storage: Any):
        db_connection_id = fine_tuning_request.db_connection_id
        repository = TableDescriptionRepository(storage)
        db_scan = repository.get_all_tables_by_db(
            {
                "db_connection_id": ObjectId(db_connection_id),
                "status": TableDescriptionStatus.SYNCHRONIZED.value,
            }
        )
        golden_records_repository = GoldenRecordRepository(storage)
        database_schema = cls.format_dataset(db_scan)
        cls.finetuning_dataset_path = f"tmp/{str(uuid.uuid4())}.jsonl"
        for golden_record_id in fine_tuning_request.golden_records:
            golden_record = golden_records_repository.find_by_id(golden_record_id)
            question = golden_record.question
            query = golden_record.sql_query
            system_prompt = FINETUNING_SYSTEM_INFORMATION + database_schema
            user_prompt = "User Question: " + question + "\n SQL: "
            assistant_prompt = query + "\n"
            with open(cls.finetuning_dataset_path, "a") as outfile:
                messages = {
                    "messages": [
                        {"role": "system", "content": f"{system_prompt}"},
                        {"role": "user", "content": f"Question : {user_prompt}"},
                        {"role": "assistant", "content": f"{assistant_prompt}"},
                    ]
                }
                json.dump(messages, outfile)
                outfile.write("\n")
        db_connection_repository = DatabaseConnectionRepository(storage)
        db_connection = db_connection_repository.find_by_id(
            fine_tuning_request.db_connection_id
        )
        openai.api_key = db_connection.decrypt_api_key()
        model_repository = FinetuningsRepository(storage)
        model = model_repository.find_by_id(fine_tuning_request.id)
        model.finetuning_file_id = openai.File.create(
            file=open(cls.finetuning_dataset_path, purpose="fine-tune")
        )["id"]
        model_repository.update(model)
        os.remove(cls.finetuning_dataset_path)

    @classmethod
    def create_fine_tuning_job(cls, fine_tuning_request: Finetuning, storage: Any):
        db_connection_repository = DatabaseConnectionRepository(storage)
        db_connection = db_connection_repository.find_by_id(
            fine_tuning_request.db_connection_id
        )
        openai.api_key = db_connection.decrypt_api_key()
        model_repository = FinetuningsRepository(storage)
        model = model_repository.find_by_id(fine_tuning_request.id)
        retrieve_file_attempt = 0
        while True:
            if (
                openai.File.retrieve(id=model.finetuning_file_id)["status"]
                == "processed"
            ):
                break
            time.sleep(5)
            retrieve_file_attempt += 1
            if retrieve_file_attempt == FILE_PROCESSING_ATTEMPTS:
                model.status = "failed"
                model.error = "File processing failed"
                model_repository.update(model)
                return
        finetuning_request = openai.FineTune.create(
            training_file=model.finetuning_file_id,
            model=model.base_llm.model_name,
            hyperparameters=model.base_llm.model_parameters,
        )
        model.finetuning_job_id = finetuning_request["id"]
        if finetuning_request["status"] == "failed":
            model.error = "Fine tuning failed before starting"
        model.status = finetuning_request["status"]
        model_repository.update(model)

    @classmethod
    def retrieve_finetuning_job(cls, fine_tuning_request: Finetuning, storage: Any):
        db_connection_repository = DatabaseConnectionRepository(storage)
        db_connection = db_connection_repository.find_by_id(
            fine_tuning_request.db_connection_id
        )
        openai.api_key = db_connection.decrypt_api_key()
        model_repository = FinetuningsRepository(storage)
        model = model_repository.find_by_id(fine_tuning_request.id)
        finetuning_request = openai.FineTune.retrieve(id=model.finetuning_job_id)
        if finetuning_request["status"] == "failed":
            model.error = "Fine tuning failed during processing by OpenAI"
        model.status = finetuning_request["status"]
        model_repository.update(model)

    @classmethod
    def cancel_finetuning_job(cls, fine_tuning_request: Finetuning, storage: Any):
        db_connection_repository = DatabaseConnectionRepository(storage)
        db_connection = db_connection_repository.find_by_id(
            fine_tuning_request.db_connection_id
        )
        openai.api_key = db_connection.decrypt_api_key()
        model_repository = FinetuningsRepository(storage)
        model = model_repository.find_by_id(fine_tuning_request.id)
        finetuning_request = openai.FineTune.cancel(id=model.finetuning_job_id)
        model.status = finetuning_request["status"]
        model.error = "Fine tuning cancelled by the user"
        model_repository.update(model)
