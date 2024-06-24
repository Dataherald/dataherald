import json
import logging
import os
import time
import uuid
from typing import Any, List

import numpy as np
import tiktoken
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from openai import OpenAI
from overrides import override
from sql_metadata import Parser
from tiktoken import Encoding

from dataherald.config import System
from dataherald.db_scanner.models.types import TableDescription, TableDescriptionStatus
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.finetuning import FinetuningModel
from dataherald.repositories.database_connections import DatabaseConnectionRepository
from dataherald.repositories.finetunings import FinetuningsRepository
from dataherald.repositories.golden_sqls import GoldenSQLRepository
from dataherald.types import Finetuning, FineTuningStatus
from dataherald.utils.agent_prompts import FINETUNING_SYSTEM_INFORMATION
from dataherald.utils.models_context_window import OPENAI_FINETUNING_MODELS_WINDOW_SIZES

FILE_PROCESSING_ATTEMPTS = 20
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL","text-embedding-3-large")
CATEGORICAL_COLUMNS_THRESHOLD = 60

logger = logging.getLogger(__name__)


class OpenAIFineTuning(FinetuningModel):
    encoding: Encoding
    fine_tuning_model: Finetuning
    storage: Any
    client: OpenAI

    def __init__(self, system: System, storage: Any, fine_tuning_model: Finetuning):
        self.storage = storage
        self.system = system
        self.fine_tuning_model = fine_tuning_model
        db_connection_repository = DatabaseConnectionRepository(storage)
        db_connection = db_connection_repository.find_by_id(
            fine_tuning_model.db_connection_id
        )
        if self.system.settings["azure_api_key"] is not None:
            self.embedding = AzureOpenAIEmbeddings(
                azure_api_key=db_connection.decrypt_api_key(),
                model=EMBEDDING_MODEL,
            )
        else:
            self.embedding = OpenAIEmbeddings(
                openai_api_key=db_connection.decrypt_api_key(),
                model=EMBEDDING_MODEL,
            )
        self.encoding = tiktoken.encoding_for_model(
            fine_tuning_model.base_llm.model_name
        )
        self.client = OpenAI(api_key=db_connection.decrypt_api_key())

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        return round(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), 4)

    @staticmethod
    def map_finetuning_status(status: str) -> str:
        mapped_statuses = {
            "queued": FineTuningStatus.QUEUED.value,
            "running": FineTuningStatus.RUNNING.value,
            "succeeded": FineTuningStatus.SUCCEEDED.value,
            "failed": FineTuningStatus.FAILED.value,
            "cancelled": FineTuningStatus.CANCELLED.value,
            "validating_files": FineTuningStatus.VALIDATING_FILES.value,
        }
        if status not in mapped_statuses:
            return FineTuningStatus.QUEUED.value
        return mapped_statuses[status]

    @staticmethod
    def _filter_tables_by_schema(db_scan: List[TableDescription], schemas: List[str]):
        if schemas:
            return [table for table in db_scan if table.schema_name in schemas]
        return db_scan

    def format_columns(
        self, table: TableDescription, top_k: int = CATEGORICAL_COLUMNS_THRESHOLD
    ) -> str:
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
            categories = column.categories
            categories_text = ""
            if categories:
                if len(categories) <= top_k:
                    categories_text = f"Categories: {categories},"
            if categories_text:
                columns_information += f"{name}: {categories_text}\n"
        return columns_information

    def format_table(self, table: TableDescription) -> str:
        table_representation = ""
        table_representation += table.table_schema + "\n"
        descriptions = []
        if table.description is not None:
            descriptions.append(f"Table `{table.table_name}`: {table.description}\n")
            for column in table.columns:
                if column.description is not None:
                    descriptions.append(
                        f"Column `{column.name}`: {column.description}\n"
                    )
        if len(descriptions) > 0:
            table_representation += f"/*\n{''.join(descriptions)}*/\n"
        columns_information = self.format_columns(table)
        if columns_information:
            table_representation += "/* Categorical Columns:\n"
            table_representation += columns_information
            table_representation += "*/\n"
        sample_rows = table.examples
        table_representation += "/* Sample rows:\n"
        for item in sample_rows:
            for key, value in item.items():
                table_representation += f"{key}: {value}, "
            table_representation += "*/\n"
        table_representation += "\n\n"
        return table_representation

    def create_table_representation(self, table: TableDescription) -> str:
        col_rep = ""
        for column in table.columns:
            if column.description is not None:
                col_rep += f"{column.name}: {column.description}, "
            else:
                col_rep += f"{column.name}, "
        if table.description is not None:
            table_rep = f"Table {table.table_name} contain columns: [{col_rep}], this tables has: {table.description}"
        else:
            table_rep = f"Table {table.table_name} contain columns: [{col_rep}]"
        return table_rep

    def sort_tables(
        self,
        tables: List[TableDescription],
        table_embeddings: List[List[float]],
        prompt: str,
    ) -> List[TableDescription]:
        tables_with_similarity = []
        prompt_embedding = self.embedding.embed_query(prompt)
        similarities = np.dot(table_embeddings, prompt_embedding) / (
            np.linalg.norm(table_embeddings) * np.linalg.norm(prompt_embedding)
        )
        for i in range(len(tables)):
            tables_with_similarity.append((tables[i], similarities[i]))
        tables_with_similarity.sort(key=lambda x: x[1], reverse=True)
        return [table[0] for table in tables_with_similarity]

    def format_dataset(
        self,
        db_scan: List[TableDescription],
        table_embeddings: List[List[float]],
        prompt: str,
        token_limit: int,
        correct_tables: [str] = None,  # type: ignore
    ) -> str:
        schema_of_database = ""
        indexes_to_remove = []
        for i in range(len(db_scan)):
            table = db_scan[i]
            if correct_tables and table.table_name in correct_tables:
                schema_of_database += self.format_table(table)
                indexes_to_remove.append(i)
        new_db_scan = []
        new_table_embeddings = []
        for i in range(len(db_scan)):
            if i not in indexes_to_remove:
                new_db_scan.append(db_scan[i])
                new_table_embeddings.append(table_embeddings[i])
        db_scan = self.sort_tables(new_db_scan, new_table_embeddings, prompt)
        for table in db_scan:
            next_table = self.format_table(table)
            if len(schema_of_database) + len(next_table) < token_limit:
                schema_of_database = next_table + schema_of_database
            else:
                break
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
                "db_connection_id": str(db_connection_id),
                "status": TableDescriptionStatus.SCANNED.value,
            }
        )
        db_scan = self._filter_tables_by_schema(db_scan, self.fine_tuning_model.schemas)
        golden_sqls_repository = GoldenSQLRepository(self.storage)
        finetuning_dataset_path = f"tmp/{str(uuid.uuid4())}.jsonl"
        model_repository = FinetuningsRepository(self.storage)
        model = model_repository.find_by_id(self.fine_tuning_model.id)
        results = []
        table_representations = []
        for table in db_scan:
            table_representations.append(self.create_table_representation(table))
        table_embeddings = self.embedding.embed_documents(table_representations)
        for index, golden_sql_id in enumerate(self.fine_tuning_model.golden_sqls):
            logger.info(
                f"Processing golden sql {index + 1} of {len(self.fine_tuning_model.golden_sqls)}"
            )
            golden_sql = golden_sqls_repository.find_by_id(golden_sql_id)
            question = golden_sql.prompt_text
            query = golden_sql.sql
            margin_tokens = len(self.encoding.encode(question + query)) + 100
            correct_tables_unformatted = Parser(query).tables
            correct_tables = []
            for table in correct_tables_unformatted:
                correct_tables.append(table.split(".")[-1])
            database_schema = self.format_dataset(
                db_scan=list(db_scan),
                table_embeddings=table_embeddings,
                prompt=question,
                token_limit=OPENAI_FINETUNING_MODELS_WINDOW_SIZES[
                    self.fine_tuning_model.base_llm.model_name
                ]
                - margin_tokens,
                correct_tables=correct_tables,
            )
            system_prompt = FINETUNING_SYSTEM_INFORMATION + database_schema
            user_prompt = "User Question: " + question + "\n SQL: "
            assistant_prompt = query + "\n"
            results.append(
                {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                        {"role": "assistant", "content": assistant_prompt},
                    ]
                }
            )
        with open(finetuning_dataset_path, "a") as outfile:
            for messages in results:
                number_of_tokens = self.count_tokens(messages)
                if (
                    number_of_tokens
                    > OPENAI_FINETUNING_MODELS_WINDOW_SIZES[
                        self.fine_tuning_model.base_llm.model_name
                    ]
                ):
                    model.status = FineTuningStatus.FAILED.value
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
        if model.status == FineTuningStatus.FAILED.value:
            return
        if self.check_file_status(model.finetuning_file_id):
            finetuning_request = self.client.fine_tuning.jobs.create(
                training_file=model.finetuning_file_id,
                model=model.base_llm.model_name,
                hyperparameters=(
                    model.base_llm.model_parameters
                    if model.base_llm.model_parameters
                    else {
                        "batch_size": 1,
                        "learning_rate_multiplier": "auto",
                        "n_epochs": 3,
                    }
                ),
            )
            model.finetuning_job_id = finetuning_request.id
            if finetuning_request.status == "failed":
                model.error = "Fine tuning failed before starting"
            model.status = self.map_finetuning_status(finetuning_request.status)
            model_repository.update(model)
        else:
            model.status = FineTuningStatus.FAILED.value
            model.error = "File processing failed"
            model_repository.update(model)

    @override
    def retrieve_finetuning_job(self) -> Finetuning:
        model_repository = FinetuningsRepository(self.storage)
        model = model_repository.find_by_id(self.fine_tuning_model.id)
        if model.finetuning_job_id is not None:
            finetuning_request = self.client.fine_tuning.jobs.retrieve(
                fine_tuning_job_id=model.finetuning_job_id
            )
            if finetuning_request.status == "failed":
                model.error = finetuning_request.error.message
            model.status = self.map_finetuning_status(finetuning_request.status)
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
        model.status = self.map_finetuning_status(finetuning_request.status)
        model.error = "Fine tuning cancelled by the user"
        model_repository.update(model)
        return model
