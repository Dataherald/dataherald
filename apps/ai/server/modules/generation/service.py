from datetime import datetime

import httpx
from fastapi.responses import StreamingResponse

from config import settings
from exceptions.exception_handlers import raise_engine_exception
from modules.db_connection.service import DBConnectionService
from modules.generation.models.entities import (
    DHNLGenerationMetadata,
    DHPromptMetadata,
    DHSQLGenerationMetadata,
    GenerationSource,
    GenerationStatus,
    NLGeneration,
    NLGenerationMetadata,
    Prompt,
    PromptMetadata,
    SQLGeneration,
    SQLGenerationMetadata,
    SQLGenerationStatus,
)
from modules.generation.models.exceptions import (
    GenerationVerifiedOrRejectedError,
    InvalidSqlGenerationError,
    NlGenerationNotFoundError,
    PromptNotFoundError,
    SqlGenerationNotFoundError,
)
from modules.generation.models.requests import (
    NLGenerationRequest,
    PromptRequest,
    PromptSQLGenerationRequest,
    PromptSQLNLGenerationRequest,
    SQLGenerationRequest,
    SQLNLGenerationRequest,
)
from modules.generation.models.responses import (
    NLGenerationResponse,
    PromptResponse,
    SQLGenerationResponse,
)
from modules.generation.repository import GenerationRepository
from utils.analytics import Analytics, EventName, EventType
from utils.misc import reserved_key_in_metadata


class GenerationService:
    def __init__(self):
        self.repo = GenerationRepository()
        self.db_connection_service = DBConnectionService()
        self.analytics = Analytics()

    def get_prompt(self, prompt_id: str, org_id: str) -> PromptResponse:
        return self.get_prompt_in_org(prompt_id, org_id)

    def get_prompts(
        self,
        page: int,
        page_size: int,
        order: str,
        ascend: bool,
        org_id: str,
        db_connection_id: str = None,
    ) -> list[PromptResponse]:
        return self.repo.get_prompts(
            skip=page * page_size,
            limit=page_size,
            order=order,
            ascend=ascend,
            org_id=org_id,
            db_connection_id=db_connection_id,
        )

    def get_sql_generation(
        self, sql_generation_id: str, org_id: str
    ) -> SQLGenerationResponse:
        return self.get_sql_generation_in_org(sql_generation_id, org_id)

    def get_sql_generations(
        self,
        page: int,
        page_size: int,
        order: str,
        ascend: bool,
        org_id: str,
        prompt_id: str = None,
    ) -> list[SQLGenerationResponse]:
        return self.repo.get_sql_generations(
            skip=page * page_size,
            limit=page_size,
            order=order,
            ascend=ascend,
            org_id=org_id,
            prompt_id=prompt_id,
        )

    def get_nl_generation(
        self, nl_generation_id: str, org_id: str
    ) -> NLGenerationResponse:
        return self.get_nl_generation_in_org(nl_generation_id, org_id)

    def get_nl_generations(
        self,
        page: int,
        page_size: int,
        order: str,
        ascend: bool,
        org_id: str,
        sql_generation_id: str = None,
    ) -> list[NLGenerationResponse]:
        return self.repo.get_nl_generations(
            skip=page * page_size,
            limit=page_size,
            order=order,
            ascend=ascend,
            org_id=org_id,
            sql_generation_id=sql_generation_id,
        )

    async def create_prompt(
        self, create_request: PromptRequest, org_id: str
    ) -> PromptResponse:
        reserved_key_in_metadata(create_request.metadata)
        self.db_connection_service.get_db_connection_in_org(
            create_request.db_connection_id, org_id
        )

        create_request.metadata = PromptMetadata(
            **create_request.metadata,
            dh_internal=self._initialize_prompt_dh_metadata(org_id),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/prompts",
                json=create_request.dict(exclude_unset=True),
            )
            raise_engine_exception(response, org_id=org_id)
            return PromptResponse(**response.json())

    async def create_prompt_sql_generation(
        self, create_request: PromptSQLGenerationRequest, org_id: str
    ) -> SQLGenerationResponse:
        reserved_key_in_metadata(create_request.prompt.metadata)
        reserved_key_in_metadata(create_request.metadata)
        self.db_connection_service.get_db_connection_in_org(
            create_request.prompt.db_connection_id, org_id
        )

        create_request.metadata = SQLGenerationMetadata(
            **create_request.metadata,
            dh_internal=DHSQLGenerationMetadata(organization_id=org_id),
        )
        create_request.prompt.metadata = PromptMetadata(
            **create_request.prompt.metadata,
            dh_internal=self._initialize_prompt_dh_metadata(org_id),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/prompts/sql-generations",
                json=create_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            sql_generation = SQLGenerationResponse(**response.json())

            self._update_generation_status(
                sql_generation.prompt_id, sql_generation.status
            )

            self._track_sql_generation_created_event(org_id, sql_generation)

            return sql_generation

    async def create_prompt_sql_generation_stream(
        self, create_request: PromptSQLGenerationRequest, org_id: str
    ):
        reserved_key_in_metadata(create_request.prompt.metadata)
        reserved_key_in_metadata(create_request.metadata)
        self.db_connection_service.get_db_connection_in_org(
            create_request.prompt.db_connection_id, org_id
        )
        create_request.metadata = SQLGenerationMetadata(
            **create_request.metadata,
            dh_internal=DHSQLGenerationMetadata(organization_id=org_id),
        )
        create_request.prompt.metadata = PromptMetadata(
            **create_request.prompt.metadata,
            dh_internal=self._initialize_prompt_dh_metadata(org_id),
        )
        created_at = datetime.now()
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                url=settings.engine_url + "/stream-sql-generation",
                json=create_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

        self._track_sql_generation_created_event(
            org_id, SQLGeneration(created_at=created_at, completed_at=datetime.now())
        )

    async def create_prompt_sql_nl_generation(
        self, create_request: PromptSQLNLGenerationRequest, org_id: str
    ) -> NLGenerationResponse:
        reserved_key_in_metadata(create_request.sql_generation.prompt.metadata)
        reserved_key_in_metadata(create_request.sql_generation.metadata)
        reserved_key_in_metadata(create_request.metadata)
        self.db_connection_service.get_db_connection_in_org(
            create_request.sql_generation.prompt.db_connection_id, org_id
        )

        create_request.sql_generation.prompt.metadata = PromptMetadata(
            **create_request.sql_generation.prompt.metadata,
            dh_internal=self._initialize_prompt_dh_metadata(org_id),
        )
        create_request.sql_generation.metadata = SQLGenerationMetadata(
            **create_request.sql_generation.metadata,
            dh_internal=DHSQLGenerationMetadata(organization_id=org_id),
        )
        create_request.metadata = NLGenerationMetadata(
            **create_request.metadata,
            dh_internal=DHNLGenerationMetadata(organization_id=org_id),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/prompts/sql-generations/nl-generations",
                json=create_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            nl_generation = NLGenerationResponse(**response.json())
            sql_generation = self.repo.get_sql_generation(
                nl_generation.sql_generation_id, org_id
            )

            self._update_generation_status(
                sql_generation.prompt_id, sql_generation.status
            )

            self._track_sql_generation_created_event(org_id, sql_generation)

            return nl_generation

    async def create_sql_generation(
        self, prompt_id: str, create_request: SQLGenerationRequest, org_id: str
    ) -> SQLGenerationResponse:
        reserved_key_in_metadata(create_request.metadata)
        prompt = self.get_prompt_in_org(prompt_id, org_id)
        if prompt.metadata.dh_internal.generation_status in {
            GenerationStatus.REJECTED,
            GenerationStatus.VERIFIED,
        }:
            raise GenerationVerifiedOrRejectedError(prompt_id, org_id)
        create_request.metadata = SQLGenerationMetadata(
            **create_request.metadata,
            dh_internal=DHSQLGenerationMetadata(organization_id=org_id),
        )
        self.repo.update_prompt_dh_metadata(
            prompt_id,
            DHPromptMetadata(generation_status=GenerationStatus.INITIALIZED),
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + f"/prompts/{prompt_id}/sql-generations",
                json=create_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            sql_generation = SQLGenerationResponse(**response.json())

            self._update_generation_status(prompt_id, sql_generation.status)

            self._track_sql_generation_created_event(org_id, sql_generation)

            return sql_generation

    async def create_sql_nl_generation(
        self, prompt_id: str, create_request: SQLNLGenerationRequest, org_id: str
    ) -> NLGenerationResponse:
        reserved_key_in_metadata(create_request.sql_generation.metadata)
        reserved_key_in_metadata(create_request.metadata)
        prompt = self.get_prompt_in_org(prompt_id, org_id)
        if prompt.metadata.dh_internal.generation_status in {
            GenerationStatus.REJECTED,
            GenerationStatus.VERIFIED,
        }:
            raise GenerationVerifiedOrRejectedError(prompt_id, org_id)
        create_request.sql_generation.metadata = SQLGenerationMetadata(
            **create_request.sql_generation.metadata,
            dh_internal=DHSQLGenerationMetadata(organization_id=org_id),
        )
        create_request.metadata = NLGenerationMetadata(
            **create_request.metadata,
            dh_internal=DHNLGenerationMetadata(organization_id=org_id),
        )

        self.repo.update_prompt_dh_metadata(
            prompt_id,
            DHPromptMetadata(generation_status=GenerationStatus.INITIALIZED),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url
                + f"/prompts/{prompt_id}/sql-generations/nl-generations",
                json=create_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            nl_generation = NLGenerationResponse(**response.json())
            sql_generation = self.repo.get_sql_generation(
                nl_generation.sql_generation_id, org_id
            )

            self._update_generation_status(prompt_id, sql_generation.status)

            self._track_sql_generation_created_event(org_id, sql_generation)

            return nl_generation

    async def create_nl_generation(
        self, sql_generation_id: str, create_request: NLGenerationRequest, org_id: str
    ) -> NLGenerationResponse:
        reserved_key_in_metadata(create_request.metadata)
        self.get_sql_generation_in_org(sql_generation_id, org_id)

        create_request.metadata = NLGenerationMetadata(
            **create_request.metadata,
            dh_internal=DHNLGenerationMetadata(organization_id=org_id),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url
                + f"/sql-generations/{sql_generation_id}/nl-generations",
                json=create_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            return NLGenerationResponse(**response.json())

    async def execute_sql_generation(
        self,
        sql_generation_id: str,
        max_rows: int,
        org_id: str,
    ) -> list[dict]:
        sql_generation = self.get_sql_generation_in_org(sql_generation_id, org_id)
        if sql_generation.status != SQLGenerationStatus.VALID:
            raise InvalidSqlGenerationError(sql_generation_id, org_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.engine_url + f"/sql-generations/{sql_generation_id}/execute",
                params={"max_rows": max_rows},
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            return response.json()

    async def export_csv_file(
        self, sql_generation_id: str, org_id: str
    ) -> StreamingResponse:
        sql_generation = self.get_sql_generation_in_org(sql_generation_id, org_id)
        if sql_generation.status != SQLGenerationStatus.VALID:
            raise InvalidSqlGenerationError(sql_generation_id, org_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.engine_url + f"/sql-generations/{sql_generation_id}/csv-file",
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            return StreamingResponse(
                content=response.iter_bytes(),
                headers=response.headers,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "text/csv"),
            )

    def get_prompt_in_org(self, prompt_id: str, org_id: str) -> Prompt:
        prompt = self.repo.get_prompt(prompt_id, org_id)
        if not prompt:
            raise PromptNotFoundError(prompt_id, org_id)
        return prompt

    def get_sql_generation_in_org(
        self, sql_generation_id: str, org_id: str
    ) -> SQLGeneration:
        sql_generation = self.repo.get_sql_generation(sql_generation_id, org_id)
        if not sql_generation:
            raise SqlGenerationNotFoundError(sql_generation_id, org_id)
        return sql_generation

    def get_nl_generation_in_org(
        self, nl_generation_id: str, org_id: str
    ) -> NLGeneration:
        nl_generation = self.repo.get_nl_generation(nl_generation_id, org_id)
        if not nl_generation:
            raise NlGenerationNotFoundError(nl_generation_id, org_id)
        return nl_generation

    def _update_generation_status(self, prompt_id: str, status: SQLGenerationStatus):
        self.repo.update_prompt_dh_metadata(
            prompt_id,
            DHPromptMetadata(
                generation_status=(
                    GenerationStatus.NOT_VERIFIED
                    if status == SQLGenerationStatus.VALID
                    else GenerationStatus.ERROR
                )
            ),
        )

    def _initialize_prompt_dh_metadata(self, org_id: str) -> DHPromptMetadata:
        return DHPromptMetadata(
            organization_id=org_id,
            display_id=self.repo.get_next_display_id(org_id),
            generation_status=GenerationStatus.INITIALIZED,
            source=GenerationSource.API,
        )

    def _track_sql_generation_created_event(
        self, org_id: str, sql_generation: SQLGeneration
    ):
        self.analytics.track(
            org_id,
            EventName.sql_generation_created,
            EventType.sql_generation_event(
                id=sql_generation.id,
                organization_id=org_id,
                status=sql_generation.status,
                source=GenerationSource.API,
                confidence_score=sql_generation.confidence_score,
                execution_time=(
                    sql_generation.completed_at - sql_generation.created_at
                ).total_seconds(),
            ),
        )
