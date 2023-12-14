import json
import logging
import os
import time
import uuid
from typing import Any, List

import tiktoken
from bson.objectid import ObjectId
from openai import OpenAI
from overrides import override
from tiktoken import Encoding

from dataherald.db_scanner.models.types import TableDescription, TableDescriptionStatus
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.finetuning import FinetuningModel
from dataherald.repositories.database_connections import DatabaseConnectionRepository
from dataherald.repositories.finetunings import FinetuningsRepository
from dataherald.repositories.golden_records import GoldenRecordRepository
from dataherald.types import Finetuning
from dataherald.utils.agent_prompts import FINETUNING_SYSTEM_INFORMATION
from dataherald.utils.models_context_window import OPENAI_CONTEXT_WIDNOW_SIZES

FILE_PROCESSING_ATTEMPTS = 20

logger = logging.getLogger(__name__)


class OpenAIFineTuning(FinetuningModel):
    encoding: Encoding
    fine_tuning_model: Finetuning
    storage: Any
    client: OpenAI

    def __init__(self, storage: Any, fine_tuning_model: Finetuning):
        self.storage = storage
        self.fine_tuning_model = fine_tuning_model
        db_connection_repository = DatabaseConnectionRepository(storage)
        db_connection = db_connection_repository.find_by_id(
            fine_tuning_model.db_connection_id
        )
        self.encoding = tiktoken.encoding_for_model(
            fine_tuning_model.base_llm.model_name
        )
        self.client = OpenAI(api_key=db_connection.decrypt_api_key())

    @classmethod
    def format_columns(cls, table: TableDescription, top_k: int = 100) -> str:
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

    @classmethod
    def format_dataset(cls, db_scan: List[TableDescription]) -> str:
        schema_of_database = ""
        for table in db_scan:
            tables_schema = table.table_schema
            schema_of_database += f"{tables_schema}\n"
            schema_of_database += "# Categorical Columns:\n"
            columns_information = cls.format_columns(table)
            schema_of_database += columns_information
            sample_rows = table.examples
            schema_of_database += "# Sample rows:\n"
            for item in sample_rows:
                for key, value in item.items():
                    schema_of_database += f"{key}: {value}, "
                schema_of_database += "\n"
            schema_of_database += "\n\n"
        return schema_of_database

    @override
    def count_tokens(self, messages: dict) -> int:
        prompt = ""
        for message in messages["messages"]:
            prompt += message["content"]
        return len(self.encoding.encode(prompt))

    @override
    def create_fintuning_dataset(self):
        db_connection_id = self.fine_tuning_model.db_connection_id
        repository = TableDescriptionRepository(self.storage)
        db_scan = repository.get_all_tables_by_db(
            {
                "db_connection_id": ObjectId(db_connection_id),
                "status": TableDescriptionStatus.SYNCHRONIZED.value,
            }
        )
        golden_records_repository = GoldenRecordRepository(self.storage)
        database_schema = self.format_dataset(db_scan)
        finetuning_dataset_path = f"tmp/{str(uuid.uuid4())}.jsonl"
        model_repository = FinetuningsRepository(self.storage)
        model = model_repository.find_by_id(self.fine_tuning_model.id)
        for golden_record_id in self.fine_tuning_model.golden_records:
            golden_record = golden_records_repository.find_by_id(golden_record_id)
            question = golden_record.question
            query = golden_record.sql_query
            system_prompt = FINETUNING_SYSTEM_INFORMATION + database_schema
            user_prompt = "User Question: " + question + "\n SQL: "
            assistant_prompt = query + "\n"
            with open(finetuning_dataset_path, "a") as outfile:
                messages = {
                    "messages": [
                        {"role": "system", "content": f"{system_prompt}"},
                        {"role": "user", "content": f"Question : {user_prompt}"},
                        {"role": "assistant", "content": f"{assistant_prompt}"},
                    ]
                }
                number_of_tokens = self.count_tokens(messages)
                if (
                    number_of_tokens
                    > OPENAI_CONTEXT_WIDNOW_SIZES[
                        self.fine_tuning_model.base_llm.model_name
                    ]
                ):
                    model.status = "failed"
                    model.error = "The number of tokens in the prompt is too large"
                    model_repository.update(model)
                    os.remove(finetuning_dataset_path)
                    return
                json.dump(messages, outfile)
                outfile.write("\n")
        model.finetuning_file_id = self.client.files.create(
            file=open(finetuning_dataset_path, "rb"), purpose="fine-tune"
        ).id
        model_repository.update(model)
        os.remove(finetuning_dataset_path)

    def check_file_status(self, file_id: str) -> bool:
        retrieve_file_attempt = 0
        while True:
            file_info = self.client.files.retrieve(file_id=file_id)
            if file_info.status == "processed":
                return True
            time.sleep(5)
            retrieve_file_attempt += 1
            if retrieve_file_attempt == FILE_PROCESSING_ATTEMPTS:
                return False

    @override
    def create_fine_tuning_job(self):
        model_repository = FinetuningsRepository(self.storage)
        model = model_repository.find_by_id(self.fine_tuning_model.id)
        if self.check_file_status(model.finetuning_file_id):
            finetuning_request = self.client.fine_tuning.jobs.create(
                training_file=model.finetuning_file_id,
                model=model.base_llm.model_name,
                hyperparameters=model.base_llm.model_parameters
                if model.base_llm.model_parameters
                else {
                    "batch_size": 1,
                    "learning_rate_multiplier": "auto",
                    "n_epochs": 3,
                },
            )
            model.finetuning_job_id = finetuning_request.id
            if finetuning_request.status == "failed":
                model.error = "Fine tuning failed before starting"
            model.status = finetuning_request.status
            model_repository.update(model)
        else:
            model.status = "failed"
            model.error = "File processing failed"
            model_repository.update(model)

    @override
    def retrieve_finetuning_job(self) -> Finetuning:
        model_repository = FinetuningsRepository(self.storage)
        model = model_repository.find_by_id(self.fine_tuning_model.id)
        finetuning_request = self.client.fine_tuning.jobs.retrieve(
            fine_tuning_job_id=model.finetuning_job_id
        )
        if finetuning_request.status == "failed":
            model.error = finetuning_request.error.message
        model.status = finetuning_request.status
        if finetuning_request.fine_tuned_model:
            model.model_id = finetuning_request.fine_tuned_model
        model_repository.update(model)
        return model

    @override
    def cancel_finetuning_job(self) -> Finetuning:
        model_repository = FinetuningsRepository(self.storage)
        model = model_repository.find_by_id(self.fine_tuning_model.id)
        finetuning_request = self.client.fine_tuning.jobs.cancel(
            fine_tuning_job_id=model.finetuning_job_id
        )
        model.status = finetuning_request.status
        model.error = "Fine tuning cancelled by the user"
        model_repository.update(model)
        return model
