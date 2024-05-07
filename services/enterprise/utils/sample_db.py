from datetime import datetime

import httpx
from bson import ObjectId
from pydantic import BaseModel
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from config import (
    DATABASE_CONNECTION_COL,
    FINETUNING_COL,
    GOLDEN_SQL_COL,
    INSTRUCTION_COL,
    SAMPLE_DATABASE_COL,
    TABLE_DESCRIPTION_COL,
    settings,
)
from database.mongo import MongoDB
from exceptions.error_codes import BaseErrorCode, ErrorCodeData
from exceptions.exception_handlers import raise_engine_exception
from exceptions.exceptions import BaseError
from modules.db_connection.models.entities import DBConnection
from modules.finetuning.models.entities import Finetuning
from modules.golden_sql.models.entities import (
    DHGoldenSQLMetadata,
    GoldenSQLMetadata,
    GoldenSQLSource,
)
from modules.golden_sql.models.requests import GoldenSQLRequest
from modules.instruction.models.entities import Instruction
from modules.table_description.models.entities import TableDescription
from utils.encrypt import FernetEncrypt
from utils.misc import get_next_display_id
from utils.validation import ObjectIdString


class SampleDBErrorCode(BaseErrorCode):
    copy_mismatch = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Copy mismatch"
    )
    sample_db_not_found = ErrorCodeData(
        status_code=HTTP_404_NOT_FOUND, message="Sample DB not found"
    )


class SampleDBError(BaseError):
    ERROR_CODES: BaseErrorCode = SampleDBErrorCode


class SampleDBCopyMismatchError(SampleDBError):
    def __init__(self, sample_db_id: str, collection: str) -> None:
        super().__init__(
            error_code=SampleDBErrorCode.copy_mismatch.name,
            detail={"sample_db_id": sample_db_id, "collection": collection},
        )


class SampleDBObject(BaseModel):
    id: ObjectIdString
    name: str
    description: str
    example_prompts: list[str]
    database_connection: dict
    finetunings: list
    golden_sqls: list
    instructions: list
    table_descriptions: list
    created_at: datetime


class SampleDBNotFoundError(SampleDBError):
    def __init__(self, sample_db_id: str, org_id: str) -> None:
        super().__init__(
            error_code=SampleDBErrorCode.sample_db_not_found.name,
            detail={"sample_db_id": sample_db_id, "organization_id": org_id},
        )


class SampleDBDict(BaseModel):
    db_connection_id: ObjectIdString
    table_description_ids: list[ObjectIdString]
    instruction_ids: list[ObjectIdString]
    golden_sql_ids: list[ObjectIdString]
    finetuning_ids: list[ObjectIdString]


class SampleDB:
    def get_sample_dbs(self) -> list[SampleDBObject]:
        cursor = MongoDB.find(SAMPLE_DATABASE_COL, {})
        return [SampleDBObject(id=str(db["_id"]), **db) for db in cursor]

    def get_sample_db(self, sample_db_id: str) -> SampleDBObject:
        sample_db = MongoDB.find_one(
            SAMPLE_DATABASE_COL,
            {"_id": ObjectId(sample_db_id)},
        )
        return (
            SampleDBObject(id=str(sample_db["_id"]), **sample_db) if sample_db else None
        )

    async def add_sample_db(self, sample_db_id: str, org_id: str) -> SampleDBDict:
        engine_metadata = {"dh_internal": {"organization_id": org_id}}
        sample_db = self.get_sample_db(sample_db_id)
        if not sample_db:
            raise SampleDBNotFoundError(sample_db_id, org_id)

        database_connection = DBConnection(**sample_db.database_connection)
        database_connection.connection_uri = FernetEncrypt().encrypt(
            database_connection.connection_uri
        )
        database_connection.created_at = datetime.now()
        database_connection.metadata = engine_metadata

        new_db_id = str(
            MongoDB.insert_one(
                DATABASE_CONNECTION_COL, database_connection.dict(exclude={"id"})
            )
        )

        if not new_db_id:
            raise SampleDBCopyMismatchError(
                sample_db_id=sample_db_id,
                collection=DATABASE_CONNECTION_COL,
            )

        table_descriptions: list[TableDescription] = [
            TableDescription(
                **{k: v for k, v in td.items() if k != "last_schema_sync"},
                db_connection_id=new_db_id,
                created_at=datetime.now(),
                metadata=engine_metadata,
                last_schema_sync=datetime.now(),
            ).dict(exclude={"id"})
            for td in sample_db.table_descriptions
        ]

        table_description_ids = (
            [
                str(i)
                for i in MongoDB.insert_many(TABLE_DESCRIPTION_COL, table_descriptions)
            ]
            if table_descriptions
            else []
        )

        if len(table_description_ids) != len(sample_db.table_descriptions):
            raise SampleDBCopyMismatchError(
                sample_db_id=sample_db_id,
                collection=TABLE_DESCRIPTION_COL,
            )

        instructions = [
            Instruction(
                **i,
                db_connection_id=new_db_id,
                created_at=datetime.now(),
                metadata=engine_metadata,
            ).dict(exclude={"id"})
            for i in sample_db.instructions
        ]

        instruction_ids = (
            [str(i) for i in MongoDB.insert_many(INSTRUCTION_COL, instructions)]
            if instructions
            else []
        )

        if len(instruction_ids) != len(sample_db.instructions):
            raise SampleDBCopyMismatchError(
                sample_db_id=sample_db_id,
                collection=INSTRUCTION_COL,
            )

        finetunings = [
            Finetuning(
                **f,
                db_connection_id=new_db_id,
                created_at=datetime.now(),
                metadata=engine_metadata,
            ).dict(exclude={"id", "golden_sqls"})
            for f in sample_db.finetunings
        ]

        finetuning_ids = (
            [str(i) for i in MongoDB.insert_many(FINETUNING_COL, finetunings)]
            if finetunings
            else []
        )

        if len(finetuning_ids) != len(sample_db.finetunings):
            raise SampleDBCopyMismatchError(
                sample_db_id=sample_db_id,
                collection=FINETUNING_COL,
            )

        golden_sql_requests: list[GoldenSQLRequest] = []
        display_id = get_next_display_id(GOLDEN_SQL_COL, org_id, "GS")
        for golden_sql in sample_db.golden_sqls:
            golden_sql_request = GoldenSQLRequest(
                db_connection_id=new_db_id,
                prompt_text=golden_sql["prompt_text"],
                sql=golden_sql["sql"],
                metadata=GoldenSQLMetadata(
                    dh_internal=DHGoldenSQLMetadata(
                        organization_id=org_id,
                        source=GoldenSQLSource.USER_UPLOAD,
                        display_id=display_id,
                    )
                ),
            )
            golden_sql_requests.append(golden_sql_request)
            display_id = f"{display_id[:-5]}{(int(display_id[-5:])+1):05d}"

        if golden_sql_requests:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.engine_url + "/golden-sqls",
                    json=[
                        golden_sql_request.dict(
                            exclude_unset=True, exclude={"prompt_id"}
                        )
                        for golden_sql_request in golden_sql_requests
                    ],
                    timeout=settings.default_engine_timeout,
                )
                raise_engine_exception(response, org_id=org_id)

                response_jsons = response.json()
                golden_sql_ids = [str(i["id"]) for i in response_jsons]

                if len(golden_sql_ids) != len(golden_sql_requests):
                    raise SampleDBCopyMismatchError(
                        sample_db_id=sample_db_id,
                        collection=GOLDEN_SQL_COL,
                    )
        else:
            golden_sql_ids = []

        return SampleDBDict(
            db_connection_id=new_db_id,
            table_description_ids=table_description_ids,
            instruction_ids=instruction_ids,
            golden_sql_ids=golden_sql_ids,
            finetuning_ids=finetuning_ids,
        )
