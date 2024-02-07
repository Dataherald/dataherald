import io
from datetime import datetime

import PyPDF2
from fastapi import UploadFile

from dataherald.api.types.requests import ContextFileRequest
from dataherald.api.types.responses import ContextFileResponse
from dataherald.config import System
from dataherald.context_store import ContextStore
from dataherald.repositories.context_files import (
    ContextFileNotFoundError,
    ContextFileRepository,
)
from dataherald.repositories.database_connections import (
    DatabaseConnectionNotFoundError,
    DatabaseConnectionRepository,
)
from dataherald.types import ContextFile, FileUploadStatus

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB


class ContextFileCreationError(Exception):
    pass


class ContextFileService:
    def __init__(self, system: System, storage):
        self.system = system
        self.storage = storage
        self.context_file_repository = ContextFileRepository(storage)
        self.context_store = self.system.instance(ContextStore)

    async def create(
        self, file: UploadFile, context_file_request: ContextFileRequest
    ) -> ContextFileResponse:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(
            context_file_request.db_connection_id
        )
        if not db_connection:
            raise DatabaseConnectionNotFoundError(
                f"Database connection {context_file_request.db_connection_id} not found"
            )
        initial_context_file = ContextFile(
            db_connection_id=context_file_request.db_connection_id,
            file_name=file.filename,
            created_at=datetime.now(),
            metadata=context_file_request.metadata,
        )
        try:
            contents = await file.read()
            if len(contents) == 0:
                raise ContextFileCreationError("File is empty")
            if len(contents) > MAX_FILE_SIZE_BYTES:
                raise ContextFileCreationError(
                    f"File is too large, max size is {MAX_FILE_SIZE_BYTES} bytes"
                )
            pdf_file = io.BytesIO(contents)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            if pdf_reader.isEncrypted:
                raise ContextFileCreationError("File is encrypted")
            pdf_file.seek(0)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
            if not self.context_store.add_context_file(initial_context_file, pdf_text):
                raise ContextFileCreationError(
                    "Failed to upsert the file to vector store"
                )
            pdf_file.close()
        except Exception as e:
            raise ContextFileCreationError(str(e)) from e

        initial_context_file.file_status = FileUploadStatus.UPLOADED
        self.context_file_repository.update(initial_context_file)
        return ContextFileResponse(
            id=initial_context_file.id,
            db_connection_id=initial_context_file.db_connection_id,
            file_status=initial_context_file.file_status,
            file_name=initial_context_file.file_name,
            created_at=initial_context_file.created_at,
            metadata=initial_context_file.metadata,
        )

    def delete(self, context_file_id: str) -> dict:
        context_file = self.nl_generation_repository.find_by_id(context_file_id)
        if not context_file:
            raise ContextFileNotFoundError(f"Context file {context_file_id} not found")
        self.context_store.delete_context_file(context_file)
        self.context_file_repository.delete_by_id(context_file_id)
        return {"status": "success"}
