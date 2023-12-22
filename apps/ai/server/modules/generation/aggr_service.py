import httpx
from fastapi import HTTPException, status

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
    GenerationUpdateRequest,
    NLGenerationRequest,
    PromptRequest,
    PromptSQLGenerationRequest,
    PromptSQLNLGenerationRequest,
    SlackGenerationRequest,
    SQLGenerationExecuteRequest,
    SQLGenerationRequest,
    SQLNLGenerationRequest,
    SQLRequest,
)
from modules.generation.models.responses import (
    GenerationListResponse,
    GenerationResponse,
    GenerationSlackResponse,
    NLGenerationResponse,
)
from modules.generation.repository import GenerationRepository
from modules.golden_sql.models.requests import GoldenSQLRequest
from modules.golden_sql.service import GoldenSQLService
from modules.organization.models.responses import OrganizationResponse
from modules.organization.service import OrganizationService
from modules.user.models.entities import SlackInfo
from modules.user.models.responses import UserResponse
from modules.user.service import UserService
from utils.analytics import Analytics
from utils.exception import GenerationEngineError, raise_for_status
from utils.slack import SlackWebClient, remove_slack_mentions

CONFIDENCE_CAP = 0.95
CORRECT_RESPONSE_COUNT = 2
SLACK_CHARACTER_LIMIT = 2700


class AggrgationGenerationService:
    def __init__(self):
        self.repo = GenerationRepository()
        self.golden_sql_service = GoldenSQLService()
        self.org_service = OrganizationService()
        self.user_service = UserService()
        self.db_connection_service = DBConnectionService()
        self.analytics = Analytics()

    async def create_generation(
        self,
        slack_generation_request: SlackGenerationRequest,
        organization: OrganizationResponse,
    ) -> GenerationSlackResponse:
        question_string = remove_slack_mentions(slack_generation_request.prompt)

        created_by = (
            SlackWebClient(
                organization.slack_installation.bot.token
            ).get_user_real_name(slack_generation_request.slack_info.user_id)
            if slack_generation_request.slack_info
            else None
        )

        display_id = self.repo.get_next_display_id(organization.id)
        generation_request = PromptSQLNLGenerationRequest(
            sql_generation=PromptSQLGenerationRequest(
                prompt=PromptRequest(
                    text=question_string,
                    db_connection_id=organization.db_connection_id,
                    metadata=PromptMetadata(
                        dh_internal=DHPromptMetadata(
                            generation_status=GenerationStatus.INITIALIZED,
                            organization_id=organization.id,
                            display_id=display_id,
                            created_by=created_by,
                            slack_info=SlackInfo(
                                **slack_generation_request.slack_info.dict()
                            )
                            if slack_generation_request.slack_info
                            else None,
                        )
                    ),
                ),
                evaluate=True,
                metadata=SQLGenerationMetadata(
                    dh_internal=DHSQLGenerationMetadata(organization_id=organization.id)
                ),
            ),
            metadata=NLGenerationMetadata(
                dh_internal=DHNLGenerationMetadata(organization_id=organization.id)
            ),
        )

        # ask Prompt to k2 engine
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/prompts/sql-generations/nl-generations",
                json=generation_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            response_json = response.json()
            if not response_json["sql_generation_id"]:
                raise_for_status(response.status_code, response.text)

            nl_generation = NLGeneration(**response_json)
            sql_generation = self.repo.get_sql_generation(
                nl_generation.sql_generation_id, organization.id
            )
            prompt = self.repo.get_prompt(sql_generation.prompt_id, organization.id)

            self.repo.update_prompt_dh_metadata(
                prompt.id,
                DHPromptMetadata(
                    generation_status=GenerationStatus.NOT_VERIFIED
                    if sql_generation.status == SQLGenerationStatus.VALID
                    else GenerationStatus.ERROR,
                ),
            )

            self.analytics.track(
                slack_generation_request.slack_info.user_id
                if slack_generation_request.slack_info
                else organization.id,
                "generation_asked",
                {
                    "display_id": display_id,
                    "prompt_id": prompt.id,
                    "sql_generation_id": sql_generation.id,
                    "nl_generation_id": nl_generation.id,
                    "organization_id": organization.id,
                    "organization_name": organization.name,
                    "database_name": self.db_connection_service.get_db_connection(
                        organization.db_connection_id, organization.id
                    ).alias,
                    "confidence_score": sql_generation.confidence_score,
                    "status": sql_generation.status,
                    "asker": created_by,
                },
            )

            if response.status_code != status.HTTP_201_CREATED:
                raise GenerationEngineError(
                    response.status_code,
                    prompt.id,
                    display_id,
                    sql_generation.error,
                )

            if (
                organization.confidence_threshold == 1
                or sql_generation.confidence_score < organization.confidence_threshold
            ):
                is_above_confidence_threshold = False
            else:
                is_above_confidence_threshold = True
                self.analytics.track(
                    slack_generation_request.slack_info.user_id
                    if slack_generation_request.slack_info
                    else organization.id,
                    "generation_correct_on_first_try",
                    {
                        "display_id": display_id,
                        "prompt_id": prompt.id,
                        "sql_generation_id": sql_generation.id,
                        "nl_generation_id": nl_generation.id,
                        "organization_id": organization.id,
                        "organization_name": organization.name,
                        "database_name": self.db_connection_service.get_db_connection(
                            organization.db_connection_id, organization.id
                        ).alias,
                        "confidence_score": sql_generation.confidence_score,
                        "status": sql_generation.status,
                        "asker": created_by,
                    },
                )

            # error handling for response longer than character limit
            if len(nl_generation.text + sql_generation.sql) >= SLACK_CHARACTER_LIMIT:
                nl_generation.text = (
                    ":warning: The generated response has been truncated due to exceeding character limit. "
                    + "A full response will be returned once reviewed by the data-team admins: \n\n"
                    + nl_generation.text[
                        : max(SLACK_CHARACTER_LIMIT - len(sql_generation.sql), 0)
                    ]
                    + "..."
                )

            return GenerationSlackResponse(
                id=prompt.id,
                display_id=display_id,
                is_above_confidence_threshold=is_above_confidence_threshold,
                nl_generation_text=nl_generation.text,
                **sql_generation.dict(exclude={"id"}, exclude_unset=True),
            )

    async def generate_prompt_sql_and_execute(
        self, request: SQLGenerationExecuteRequest, org_id: str
    ):
        organization = self.org_service.get_organization(org_id)
        generation_request = PromptSQLGenerationRequest(
            prompt=PromptRequest(
                text=request.prompt,
                db_connection_id=organization.db_connection_id,
                metadata=PromptMetadata(
                    dh_internal=DHPromptMetadata(
                        generation_status=GenerationStatus.INITIALIZED,
                        organization_id=organization.id,
                    )
                ),
            ),
            evaluate=True,
            finetuning_id=request.model,
            metadata=SQLGenerationMetadata(
                dh_internal=DHSQLGenerationMetadata(organization_id=organization.id)
            ),
        )
        # ask Prompt to k2 engine
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/prompts/sql-generations",
                json=generation_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            response_json = response.json()
            if not response_json["id"]:
                raise_for_status(response.status_code, response.text)

            sql_generation = self.repo.get_sql_generation(response_json["id"], org_id)
            prompt = self.repo.get_prompt(sql_generation.prompt_id, organization.id)

            if sql_generation.status == SQLGenerationStatus.VALID:
                sql_result_response = await client.get(
                    settings.engine_url
                    + f"/sql-generations/{sql_generation.id}/execute",
                    timeout=settings.default_engine_timeout,
                )
                raise_for_status(
                    sql_result_response.status_code, sql_result_response.text
                )
                sql_result = sql_result_response.json()
                print(sql_result)
            else:
                sql_result = None

        return self._get_mapped_generation_response(
            prompt, sql_generation, None, sql_results=sql_result
        )

    def get_generation(self, prompt_id: str, org_id: str) -> GenerationResponse:
        prompt, sql_generation, nl_generation = None, None, None
        prompt = self.repo.get_prompt(prompt_id, org_id)

        if prompt:
            sql_generation = self.repo.get_latest_sql_generation(prompt.id, org_id)
            if sql_generation:
                nl_generation = self.repo.get_latest_nl_generation(
                    sql_generation.id, org_id
                )

            return self._get_mapped_generation_response(
                prompt, sql_generation, nl_generation
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
        )

    def get_generation_list(
        self,
        order: str,
        page: int,
        page_size: int,
        ascend: bool,  # noqa: ARG002
        org_id: str,
    ) -> list[GenerationListResponse]:
        prompts = self.repo.get_prompts(
            skip=page * page_size,
            limit=page_size,
            order=order,
            ascend=ascend,
            org_id=org_id,
        )

        generation_list = []

        for prompt in prompts:
            sql_generation = self.repo.get_latest_sql_generation(prompt.id, org_id)
            nl_generation = None
            if sql_generation:
                nl_generation = self.repo.get_latest_nl_generation(
                    sql_generation.id, org_id
                )
            generation_list.append(
                GenerationListResponse(
                    id=prompt.id,
                    prompt_text=prompt.text,
                    nl_generation_text=nl_generation.text if nl_generation else None,
                    confidence_score=sql_generation.confidence_score
                    if sql_generation
                    else None,
                    status=prompt.metadata.dh_internal.generation_status,
                    display_id=prompt.metadata.dh_internal.display_id,
                    created_at=prompt.created_at,
                    created_by=prompt.metadata.dh_internal.created_by or "Unknown",
                )
            )

        return generation_list

    async def update_generation(
        self,
        prompt_id: str,
        generation_request: GenerationUpdateRequest,
        org_id: str,
        user: UserResponse = None,
    ) -> GenerationResponse:
        prompt = self.repo.get_prompt(prompt_id, org_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
            )

        sql_generation = self.repo.get_latest_sql_generation(prompt_id, org_id)
        nl_generation = (
            self.repo.get_latest_nl_generation(sql_generation.id, org_id)
            if sql_generation
            else None
        )

        self.repo.update_prompt_dh_metadata(
            prompt_id,
            DHPromptMetadata(
                **generation_request.dict(exclude_unset=True),
                updated_by=self.user_service.get_user(user.id, org_id).name
                if user
                else None,
            ),
        )
        if generation_request.generation_status:
            # verified
            if (
                generation_request.generation_status == GenerationStatus.VERIFIED
                and sql_generation
            ):
                await self.golden_sql_service.add_verified_golden_sql(
                    GoldenSQLRequest(
                        db_connection_id=prompt.db_connection_id,
                        prompt_text=prompt.text,
                        sql=sql_generation.sql,
                    ),
                    org_id,
                    prompt_id,
                )

                # logic to track 1st time correct response generated by engine
                all_sql_generations = self.repo.get_sql_generations(
                    skip=0,
                    limit=100,
                    order="created_id",
                    ascend=True,
                    org_id=org_id,
                    prompt_id=prompt_id,
                )
                if all(
                    sql_gen.sql == sql_generation.sql for sql_gen in all_sql_generations
                ):
                    self.analytics.track(
                        user.email if user else org_id,
                        "verified_generation_correct_on_first_try",
                        {
                            "prompt_id": prompt_id,
                            "sql_generation_id": sql_generation.id,
                            "organization_id": org_id,
                            "display_id": prompt.metadata.dh_internal.display_id,
                            "status": generation_request.generation_status,
                            "confidence_score": sql_generation.confidence_score,
                            "database_name": self.db_connection_service.get_db_connection(
                                prompt.db_connection_id, org_id
                            ).alias,
                        },
                    )

            # rejected or not verified
            else:
                golden_sql = self.golden_sql_service.get_verified_golden_sql(prompt_id)
                if golden_sql:
                    await self.golden_sql_service.delete_golden_sql(
                        golden_sql.id, org_id, generation_request.generation_status
                    )
        self.analytics.track(
            user.email if user else org_id,
            "generation_saved",
            {
                "prompt_id": prompt_id,
                "sql_generation_id": sql_generation.id if sql_generation else None,
                "database_name": self.db_connection_service.get_db_connection(
                    prompt.db_connection_id, org_id
                ).alias,
                "display_id": prompt.metadata.dh_internal.display_id,
                "status": generation_request.generation_status,
                "confidence_score": sql_generation.confidence_score
                if sql_generation
                else None,
            },
        )

        return self._get_mapped_generation_response(
            prompt, sql_generation, nl_generation
        )

    async def create_sql_nl_generation(
        self, prompt_id: str, org_id: str, user: UserResponse = None
    ) -> GenerationResponse:
        prompt = self.repo.get_prompt(prompt_id, org_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
            )

        generation_request = SQLNLGenerationRequest(
            metadata={"organization_id": org_id},
            sql_generation=SQLGenerationRequest(
                evaluate=True,
                metadata={"organization_id": org_id},
            ),
        )

        self.repo.update_prompt_dh_metadata(
            prompt_id,
            DHPromptMetadata(generation_status=GenerationStatus.INITIALIZED),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url
                + f"/prompts/{prompt_id}/sql-generations/nl-generations",
                json=generation_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)
            nl_generation = NLGeneration(**response.json())
            sql_generation = self.repo.get_sql_generation(
                nl_generation.sql_generation_id, org_id
            )
            self.repo.update_prompt_dh_metadata(
                prompt_id,
                DHPromptMetadata(
                    message=nl_generation.text,
                    updated_by=self.user_service.get_user(user.id, org_id).name
                    if user
                    else None,
                    generation_status=GenerationStatus.NOT_VERIFIED
                    if sql_generation.status == SQLGenerationStatus.VALID
                    else GenerationStatus.ERROR,
                ),
            )

            if sql_generation.status == SQLGenerationStatus.VALID:
                sql_result_response = await client.get(
                    settings.engine_url
                    + f"/sql-generations/{sql_generation.id}/execute",
                    timeout=settings.default_engine_timeout,
                )
                raise_for_status(
                    sql_result_response.status_code, sql_result_response.text
                )
                sql_result = sql_result_response.json()
                print(sql_result)
            else:
                sql_result = None

            self.analytics.track(
                user.email if user else org_id,
                "generation_resubmitted",
                {
                    "prompt_id": prompt.id,
                    "sql_generation_id": sql_generation.id,
                    "sql_generation_status": sql_generation.status,
                    "confidence_score": sql_generation.confidence_score,
                    "database_name": self.db_connection_service.get_db_connection(
                        str(prompt.db_connection_id), org_id
                    ).alias,
                },
            )
            return self._get_mapped_generation_response(
                prompt, sql_generation, nl_generation, sql_results=sql_result
            )

    async def generate_sql_result(
        self,
        prompt_id: str,
        sql_request: SQLRequest,
        org_id,
        user: UserResponse = None,
    ) -> GenerationResponse:
        prompt = self.repo.get_prompt(prompt_id, org_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
            )

        if prompt.metadata.dh_internal.generation_status in {
            GenerationStatus.VERIFIED,
            GenerationStatus.REJECTED,
        }:
            raise_for_status(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="generation has already been verified or rejected",
            )

        generation_request = SQLGenerationRequest(
            sql=sql_request.sql,
            evaluate=False,
            metadata={"organization_id": org_id},
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + f"/prompts/{prompt_id}/sql-generations",
                json=generation_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)
            sql_generation = SQLGeneration(**response.json())

            self.repo.update_prompt_dh_metadata(
                prompt_id,
                DHPromptMetadata(
                    updated_by=self.user_service.get_user(user.id, org_id).name
                    if user
                    else None,
                    generation_status=GenerationStatus.NOT_VERIFIED
                    if sql_generation.status == SQLGenerationStatus.VALID
                    else GenerationStatus.ERROR,
                ),
            )
            if sql_generation.status == SQLGenerationStatus.VALID:
                sql_result_response = await client.get(
                    settings.engine_url
                    + f"/sql-generations/{sql_generation.id}/execute",
                    timeout=settings.default_engine_timeout,
                )
                raise_for_status(
                    sql_result_response.status_code, sql_result_response.text
                )
                sql_result = sql_result_response.json()
            else:
                sql_result = None

            self.analytics.track(
                user.email if user else org_id,
                "generation_executed",
                {
                    "prompt_id": prompt.id,
                    "sql_generation_id": sql_generation.id,
                    "sql_generation_status": sql_generation.status,
                    "confidence_score": sql_generation.confidence_score,
                    "database_name": self.db_connection_service.get_db_connection(
                        prompt.db_connection_id, org_id
                    ).alias,
                },
            )
            return self._get_mapped_generation_response(
                prompt, sql_generation, None, sql_results=sql_result
            )

    async def create_nl_generation(
        self, prompt_id: str, org_id: str
    ) -> NLGenerationResponse:
        prompt = self.repo.get_prompt(prompt_id, org_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
            )
        sql_generation = self.repo.get_latest_sql_generation(prompt_id, org_id)
        if not sql_generation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="SQL Prompt not found"
            )

        generation_request = NLGenerationRequest(
            metadata=NLGenerationMetadata(
                dh_internal=DHNLGenerationMetadata(organization_id=org_id)
            )
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url
                + f"/sql-generations/{sql_generation.id}/nl-generations",
                json=generation_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)

            nl_generation = NLGeneration(**response.json())
            self.repo.update_prompt_dh_metadata(
                prompt_id, DHPromptMetadata(message=nl_generation.text)
            )
            return nl_generation

    async def send_message(self, prompt_id: str, org_id: str):
        organization = self.org_service.get_organization(org_id)
        prompt = self.repo.get_prompt(prompt_id, org_id)
        if not prompt:
            return

        sql_generation = self.repo.get_latest_sql_generation(prompt_id, org_id)

        nl_generation = (
            self.repo.get_latest_nl_generation(sql_generation.id, org_id)
            if sql_generation
            else None
        )

        message = (
            f":wave: Hello, <@{prompt.metadata.dh_internal.slack_info.user_id}>! An Admin has reviewed {prompt.metadata.dh_internal.display_id}.\n\n"  # noqa: E501
            + f"Prompt: {prompt.text}\n\n"
            + f"Response: {prompt.metadata.dh_internal.message or (nl_generation.text if nl_generation else 'None')}\n\n"
            + f":memo: *Generated SQL Generation*: \n ```{sql_generation.sql if sql_generation else 'None'}```"
        )

        SlackWebClient(organization.slack_installation.bot.token).send_message(
            prompt.metadata.dh_internal.slack_info.channel_id,
            prompt.metadata.dh_internal.slack_info.thread_ts,
            message,
        )

    def _get_mapped_generation_response(
        self,
        prompt: Prompt,
        sql_generation: SQLGeneration | None,
        nl_generation: NLGeneration | None,
        sql_results: tuple[str, dict] | None = None,
    ) -> GenerationResponse:
        if not sql_generation:
            sql_generation = SQLGeneration(
                id=None,
                prompt_id=prompt.id,
                sql="",
                confidence_score=0,
            )

        if not nl_generation:
            nl_generation = NLGeneration(
                id=None,
                text=prompt.metadata.dh_internal.message or "",
            )

        if sql_results:
            rows = sql_results[1]["result"]
            columns = list(rows[0].keys())
            sql_results = {"columns": columns, "rows": rows}

        return GenerationResponse(
            id=prompt.id,
            db_connection_id=prompt.db_connection_id,
            status=prompt.metadata.dh_internal.generation_status,
            prompt_text=prompt.text,
            nl_generation_text=nl_generation.text,
            sql=sql_generation.sql,
            confidence_score=sql_generation.confidence_score,
            sql_generation_error=sql_generation.error,
            created_at=prompt.created_at,
            updated_at=nl_generation.created_at or sql_generation.created_at,
            sql_results=sql_results,
            **prompt.metadata.dh_internal.dict(exclude_unset=True),
        )
