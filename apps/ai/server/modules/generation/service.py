import httpx
from fastapi import HTTPException, status

from config import settings
from modules.db_connection.service import DBConnectionService
from modules.generation.models.entities import (
    DHNLGenerationMetadata,
    DHPromptMetadata,
    DHSQLGenerationMetadata,
    GenerationStatus,
    NLGenerationMetadata,
    PromptMetadata,
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
from modules.golden_sql.service import GoldenSQLService
from modules.organization.service import OrganizationService
from modules.user.service import UserService
from utils.analytics import Analytics
from utils.exception import raise_for_status
from utils.misc import reserved_key_in_metadata


class GenerationService:
    def __init__(self):
        self.repo = GenerationRepository()
        self.golden_sql_service = GoldenSQLService()
        self.org_service = OrganizationService()
        self.user_service = UserService()
        self.db_connection_service = DBConnectionService()
        self.analytics = Analytics()

    def get_prompt(self, prompt_id: str, org_id: str) -> PromptResponse:
        prompt = self.repo.get_prompt(prompt_id, org_id)
        if prompt:
            return prompt

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
        )

    def get_prompts(
        self, page: int, page_size: int, order: str, ascend: bool, org_id: str
    ) -> list[PromptResponse]:
        return self.repo.get_prompts(
            skip=page * page_size,
            limit=page_size,
            order=order,
            ascend=ascend,
            org_id=org_id,
        )

    def get_sql_generation(
        self, sql_generation_id: str, org_id: str
    ) -> SQLGenerationResponse:
        sql_generation = self.repo.get_sql_generation(sql_generation_id, org_id)
        if sql_generation:
            return sql_generation

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="SQL Generation not found"
        )

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
        nl_generation = self.repo.get_nl_generation(nl_generation_id, org_id)
        if nl_generation:
            return nl_generation
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NL Generation not found"
        )

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
        create_request.metadata = SQLGenerationMetadata(
            **create_request.metadata,
            dh_internal=DHSQLGenerationMetadata(organization_id=org_id),
        )
        create_request.prompt.metadata = PromptMetadata(
            **create_request.prompt.metadata,
            generation_status=GenerationStatus.INITIALIZED,
            organization_id=org_id,
            display_id=self.repo.get_next_display_id(org_id),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/prompts/sql-generations",
                json=create_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)
            sql_generation = SQLGenerationResponse(**response.json())
            self.repo.update_prompt_dh_metadata(
                sql_generation.prompt_id,
                {
                    "generation_status": GenerationStatus.NOT_VERIFIED
                    if sql_generation.status == SQLGenerationStatus.VALID
                    else GenerationStatus.ERROR
                },
            )
            return sql_generation

    async def create_prompt_sql_nl_generation(
        self, create_request: PromptSQLNLGenerationRequest, org_id: str
    ) -> NLGenerationResponse:
        reserved_key_in_metadata(create_request.sql_generation.prompt.metadata)
        reserved_key_in_metadata(create_request.sql_generation.metadata)
        reserved_key_in_metadata(create_request.metadata)
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
            raise_for_status(response.status_code, response.text)
            nl_generation = NLGenerationResponse(**response.json())
            sql_generation = self.repo.get_sql_generation(
                nl_generation.sql_generation_id, org_id
            )
            self.repo.update_prompt_dh_metadata(
                sql_generation.prompt_id,
                {
                    "generation_status": GenerationStatus.NOT_VERIFIED
                    if sql_generation.status == SQLGenerationStatus.VALID
                    else GenerationStatus.ERROR
                },
            )
            return nl_generation

    async def create_sql_generation(
        self, prompt_id: str, create_request: SQLGenerationRequest, org_id: str
    ) -> SQLGenerationResponse:
        reserved_key_in_metadata(create_request.metadata)
        prompt = self.repo.get_prompt(prompt_id, org_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found",
            )
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
            prompt_id, {"generation_status": GenerationStatus.INITIALIZED}
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + f"/prompts/{prompt_id}/sql-generations",
                json=create_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)
            sql_generation = SQLGenerationResponse(**response.json())
            self.repo.update_prompt_dh_metadata(
                prompt_id,
                {
                    "generation_status": GenerationStatus.NOT_VERIFIED
                    if sql_generation.status == SQLGenerationStatus.VALID
                    else GenerationStatus.ERROR
                },
            )
            return sql_generation

    async def create_nl_generation(
        self, sql_generation_id: str, create_request: NLGenerationRequest, org_id: str
    ) -> NLGenerationResponse:
        reserved_key_in_metadata(create_request.metadata)
        if not self.repo.get_sql_generation(sql_generation_id, org_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SQL Generation not found",
            )

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
        prompt = self.repo.get_prompt(prompt_id, org_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found",
            )
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
            prompt_id, {"generation_status": GenerationStatus.INITIALIZED}
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url
                + f"/prompts/{prompt_id}/sql-generations/nl-generations",
                json=create_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)
            nl_generation = NLGenerationResponse(**response.json())
            sql_generation = self.repo.get_sql_generation(
                nl_generation.sql_generation_id, org_id
            )
            self.repo.update_prompt_dh_metadata(
                prompt_id,
                {
                    "generation_status": GenerationStatus.NOT_VERIFIED
                    if sql_generation.status == SQLGenerationStatus.VALID
                    else GenerationStatus.ERROR
                },
            )
            return nl_generation

    async def execute_sql_generation(
        self,
        sql_generation_id: str,
        max_rows: int,
        org_id: str,
    ) -> tuple[str, dict]:
        if not self.repo.get_sql_generation(sql_generation_id, org_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SQL Generation not found",
            )
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.engine_url + f"/sql-generations/{sql_generation_id}/execute",
                params={"max_rows": max_rows},
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)
            return response.json()
