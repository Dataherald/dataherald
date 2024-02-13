import httpx
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse

from config import settings
from modules.db_connection.service import DBConnectionService
from modules.generation.models.entities import (
    DHNLGenerationMetadata,
    DHPromptMetadata,
    DHSQLGenerationMetadata,
    GenerationStatus,
    NLGeneration,
    NLGenerationMetadata,
    Prompt,
    PromptMetadata,
    SQLGeneration,
    SQLGenerationMetadata,
    SQLGenerationStatus,
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
from utils.exception import GenerationEngineError, raise_for_status
from utils.misc import reserved_key_in_metadata


class GenerationService:
    def __init__(self):
        self.repo = GenerationRepository()
        self.db_connection_service = DBConnectionService()

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
            dh_internal=DHPromptMetadata(
                organization_id=org_id,
                display_id=self.repo.get_next_display_id(org_id),
                generation_status=GenerationStatus.INITIALIZED,
            ),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/prompts",
                json=create_request.dict(exclude_unset=True),
            )
            raise_for_status(response.status_code, response.text)
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
            dh_internal=DHPromptMetadata(
                generation_status=GenerationStatus.INITIALIZED,
                organization_id=org_id,
                display_id=self.repo.get_next_display_id(org_id),
            ),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/prompts/sql-generations",
                json=create_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            self._raise_for_generation_status(response, org_id)
            sql_generation = SQLGenerationResponse(**response.json())
            self.repo.update_prompt_dh_metadata(
                sql_generation.prompt_id,
                DHPromptMetadata(
                    generation_status=(
                        GenerationStatus.NOT_VERIFIED
                        if sql_generation.status == SQLGenerationStatus.VALID
                        else GenerationStatus.ERROR
                    )
                ),
            )
            return sql_generation

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
            dh_internal=DHPromptMetadata(
                generation_status=GenerationStatus.INITIALIZED,
                organization_id=org_id,
                display_id=self.repo.get_next_display_id(org_id),
            ),
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
            self._raise_for_generation_status(response, org_id)
            nl_generation = NLGenerationResponse(**response.json())
            sql_generation = self.repo.get_sql_generation(
                nl_generation.sql_generation_id, org_id
            )
            self.repo.update_prompt_dh_metadata(
                sql_generation.prompt_id,
                DHPromptMetadata(
                    generation_status=(
                        GenerationStatus.NOT_VERIFIED
                        if sql_generation.status == SQLGenerationStatus.VALID
                        else GenerationStatus.ERROR
                    )
                ),
            )
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create SQL generation for a prompt that has been verified or rejected",
            )

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
            self._raise_for_generation_status(response, org_id, prompt)
            sql_generation = SQLGenerationResponse(**response.json())
            self.repo.update_prompt_dh_metadata(
                prompt_id,
                DHPromptMetadata(
                    generation_status=(
                        GenerationStatus.NOT_VERIFIED
                        if sql_generation.status == SQLGenerationStatus.VALID
                        else GenerationStatus.ERROR
                    )
                ),
            )
            return sql_generation

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
            raise_for_status(response.status_code, response.text)
            return NLGenerationResponse(**response.json())

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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create SQL generation for a prompt that has been verified or rejected",
            )
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
            self._raise_for_generation_status(response, org_id, prompt)
            nl_generation = NLGenerationResponse(**response.json())
            sql_generation = self.repo.get_sql_generation(
                nl_generation.sql_generation_id, org_id
            )
            self.repo.update_prompt_dh_metadata(
                prompt_id,
                DHPromptMetadata(
                    generation_status=(
                        GenerationStatus.NOT_VERIFIED
                        if sql_generation.status == SQLGenerationStatus.VALID
                        else GenerationStatus.ERROR
                    )
                ),
            )
            return nl_generation

    async def execute_sql_generation(
        self,
        sql_generation_id: str,
        max_rows: int,
        org_id: str,
    ) -> list[dict]:
        sql_generation = self.get_sql_generation_in_org(sql_generation_id, org_id)
        if sql_generation.status != SQLGenerationStatus.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SQL Generation is not valid",
            )
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.engine_url + f"/sql-generations/{sql_generation_id}/execute",
                params={"max_rows": max_rows},
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)
            return response.json()

    async def export_csv_file(
        self, sql_generation_id: str, org_id: str
    ) -> StreamingResponse:
        sql_generation = self.get_sql_generation_in_org(sql_generation_id, org_id)
        if sql_generation.status != SQLGenerationStatus.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SQL Generation is not valid",
            )
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.engine_url + f"/sql-generations/{sql_generation_id}/csv-file",
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)
            return StreamingResponse(
                content=response.iter_bytes(),
                headers=response.headers,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "text/csv"),
            )

    def get_prompt_in_org(self, prompt_id: str, org_id: str) -> Prompt:
        prompt = self.repo.get_prompt(prompt_id, org_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found",
            )
        return prompt

    def get_sql_generation_in_org(
        self, sql_generation_id: str, org_id: str
    ) -> SQLGeneration:
        sql_generation = self.repo.get_sql_generation(sql_generation_id, org_id)
        if not sql_generation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SQL Generation not found",
            )
        return sql_generation

    def get_nl_generation_in_org(
        self, nl_generation_id: str, org_id: str
    ) -> NLGeneration:
        nl_generation = self.repo.get_nl_generation(nl_generation_id, org_id)
        if not nl_generation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NL Generation not found",
            )
        return nl_generation

    def _raise_for_generation_status(
        self, response: httpx.Response, org_id: str, prompt: Prompt = None
    ):
        response_json = response.json()
        if response.status_code != status.HTTP_201_CREATED:
            if "prompt_id" in response_json and response_json["prompt_id"]:
                prompt = self.get_prompt(response_json["prompt_id"], org_id)
            if prompt:
                self.repo.update_prompt_dh_metadata(
                    prompt.id,
                    DHPromptMetadata(generation_status=GenerationStatus.ERROR),
                )
                raise GenerationEngineError(
                    status_code=response.status_code,
                    prompt_id=prompt.id,
                    display_id=prompt.metadata.dh_internal.display_id,
                    error_message=response_json["message"],
                )
            raise_for_status(response.status_code, response.text)
