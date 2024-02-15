from datetime import datetime

import httpx
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse

from config import settings
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
    SlackInfo,
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
from modules.user.models.responses import UserResponse
from modules.user.service import UserService
from utils.analytics import Analytics, EventName, EventType
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

    async def get_generation(self, prompt_id: str, org_id: str) -> GenerationResponse:
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
        db_connection_id: str = None,
    ) -> list[GenerationListResponse]:
        prompts = self.repo.get_prompts(
            skip=page * page_size,
            limit=page_size,
            order=order,
            ascend=ascend,
            org_id=org_id,
            db_connection_id=db_connection_id,
        )
        db_connection_dict = {
            db_connection.id: db_connection
            for db_connection in self.db_connection_service.get_db_connections(org_id)
        }

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
                    db_connection_alias=(
                        db_connection_dict[prompt.db_connection_id].alias
                        if prompt.db_connection_id in db_connection_dict
                        else None
                    ),
                    nl_generation_text=nl_generation.text if nl_generation else None,
                    sql=sql_generation.sql if sql_generation else None,
                    confidence_score=(
                        sql_generation.confidence_score if sql_generation else None
                    ),
                    status=prompt.metadata.dh_internal.generation_status,
                    display_id=prompt.metadata.dh_internal.display_id,
                    created_at=prompt.created_at,
                    created_by=prompt.metadata.dh_internal.created_by or "Unknown",
                    source=prompt.metadata.dh_internal.source,
                    slack_message_last_sent_at=prompt.metadata.dh_internal.slack_message_last_sent_at,
                )
            )

        return generation_list

    async def create_generation(
        self,
        slack_generation_request: SlackGenerationRequest,
        organization: OrganizationResponse,
    ) -> GenerationSlackResponse:
        question_string = remove_slack_mentions(slack_generation_request.prompt)

        created_by = (
            SlackWebClient(
                organization.slack_config.slack_installation.bot.token
            ).get_user_real_name(slack_generation_request.slack_info.user_id)
            if slack_generation_request.slack_info
            else None
        )

        display_id = self.repo.get_next_display_id(organization.id)
        generation_request = PromptSQLNLGenerationRequest(
            sql_generation=PromptSQLGenerationRequest(
                prompt=PromptRequest(
                    text=question_string,
                    db_connection_id=organization.slack_config.db_connection_id,
                    metadata=PromptMetadata(
                        dh_internal=DHPromptMetadata(
                            generation_status=GenerationStatus.INITIALIZED,
                            organization_id=organization.id,
                            display_id=display_id,
                            created_by=created_by,
                            source=GenerationSource.SLACK,
                            slack_info=(
                                SlackInfo(**slack_generation_request.slack_info.dict())
                                if slack_generation_request.slack_info
                                else None
                            ),
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
            self._raise_for_generation_status(response, display_id=display_id)

            nl_generation = NLGeneration(**response.json())
            sql_generation = self.repo.get_sql_generation(
                nl_generation.sql_generation_id, organization.id
            )

            self.repo.update_prompt_dh_metadata(
                sql_generation.prompt_id,
                DHPromptMetadata(
                    generation_status=(
                        GenerationStatus.NOT_VERIFIED
                        if sql_generation.status == SQLGenerationStatus.VALID
                        else GenerationStatus.ERROR
                    ),
                ),
            )
            prompt = self.repo.get_prompt(sql_generation.prompt_id, organization.id)

            self._track_sql_generation_created_event(
                organization.id, sql_generation, GenerationSource.SLACK
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
                sql=sql_generation.sql,
                display_id=display_id,
                is_above_confidence_threshold=(
                    False
                    if (
                        organization.confidence_threshold == 1
                        or sql_generation.confidence_score
                        < organization.confidence_threshold
                    )
                    else True
                ),
                nl_generation_text=nl_generation.text,
                exec_time=(
                    sql_generation.completed_at - sql_generation.created_at
                ).total_seconds(),
            )

    # playground endpoint
    async def create_prompt_sql_generation_result(
        self, request: SQLGenerationExecuteRequest, org_id: str, username: str
    ):
        organization = self.org_service.get_organization(org_id)
        display_id = self.repo.get_next_display_id(organization.id)
        generation_request = PromptSQLGenerationRequest(
            prompt=PromptRequest(
                text=request.prompt,
                db_connection_id=request.db_connection_id,
                metadata=PromptMetadata(
                    dh_internal=DHPromptMetadata(
                        generation_status=GenerationStatus.INITIALIZED,
                        organization_id=organization.id,
                        display_id=display_id,
                        created_by=username,
                        source=GenerationSource.PLAYGROUND,
                    )
                ),
            ),
            evaluate=True,
            finetuning_id=request.finetuning_id,
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
            self._raise_for_generation_status(response)

            sql_generation = SQLGeneration(**response.json())
            self.repo.update_prompt_dh_metadata(
                sql_generation.prompt_id,
                DHPromptMetadata(
                    generation_status=(
                        GenerationStatus.NOT_VERIFIED
                        if sql_generation.status == SQLGenerationStatus.VALID
                        else GenerationStatus.ERROR
                    ),
                ),
            )
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
            else:
                sql_result = None

            self._track_sql_generation_created_event(
                org_id, sql_generation, GenerationSource.PLAYGROUND
            )

        return self._get_mapped_generation_response(
            prompt, sql_generation, None, sql_result=sql_result
        )

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

            # rejected or not verified
            else:
                golden_sql = self.golden_sql_service.get_verified_golden_sql(prompt_id)
                if golden_sql:
                    await self.golden_sql_service.delete_golden_sql(
                        golden_sql.id, org_id, generation_request.generation_status
                    )

                # logic to track 1st time correct response generated by engine
                all_sql_generations = self.repo.get_sql_generations(
                    skip=0,
                    limit=100,
                    order="created_at",
                    ascend=True,
                    org_id=org_id,
                    prompt_id=prompt_id,
                )
                self.analytics.track(
                    org_id,
                    EventName.sql_generation_updated,
                    EventType.sql_generation_updated_event(
                        id=sql_generation.id,
                        organization_id=org_id,
                        generation_status=generation_request.generation_status,
                        confidence_score=sql_generation.confidence_score,
                        sql_modified=(
                            False
                            if all(
                                sql_gen.sql == sql_generation.sql
                                for sql_gen in all_sql_generations
                            )
                            else True
                        ),
                    ),
                )

        self.repo.update_prompt_dh_metadata(
            prompt_id,
            DHPromptMetadata(
                **generation_request.dict(exclude_unset=True),
                updated_by=(
                    self.user_service.get_user(user.id, org_id).name if user else None
                ),
            ),
        )

        prompt = self.repo.get_prompt(prompt_id, org_id)

        return self._get_mapped_generation_response(
            prompt, sql_generation, nl_generation
        )

    # resubmit generation
    async def create_sql_nl_generation(
        self, prompt_id: str, org_id: str, user: UserResponse = None
    ) -> GenerationResponse:
        prompt = self.repo.get_prompt(prompt_id, org_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
            )

        generation_request = SQLNLGenerationRequest(
            metadata=NLGenerationMetadata(
                dh_internal=DHNLGenerationMetadata(organization_id=org_id)
            ),
            sql_generation=SQLGenerationRequest(
                evaluate=True,
                metadata=SQLGenerationMetadata(
                    dh_internal=DHSQLGenerationMetadata(organization_id=org_id)
                ),
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
            self._raise_for_generation_status(response, prompt=prompt)
            nl_generation = NLGeneration(**response.json())
            sql_generation = self.repo.get_sql_generation(
                nl_generation.sql_generation_id, org_id
            )
            self.repo.update_prompt_dh_metadata(
                prompt_id,
                DHPromptMetadata(
                    message=nl_generation.text,
                    updated_by=(
                        self.user_service.get_user(user.id, org_id).name
                        if user
                        else None
                    ),
                    generation_status=(
                        GenerationStatus.NOT_VERIFIED
                        if sql_generation.status == SQLGenerationStatus.VALID
                        else GenerationStatus.ERROR
                    ),
                ),
            )
            prompt = self.repo.get_prompt(prompt_id, org_id)

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

            self._track_sql_generation_created_event(
                org_id, sql_generation, GenerationSource.QUERY_EDITOR_RESUBMIT
            )

            return self._get_mapped_generation_response(
                prompt, sql_generation, nl_generation, sql_result=sql_result
            )

    # run generation
    async def create_sql_generation_result(
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
            metadata=SQLGenerationMetadata(
                dh_internal=DHSQLGenerationMetadata(organization_id=org_id)
            ),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + f"/prompts/{prompt_id}/sql-generations",
                json=generation_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            self._raise_for_generation_status(response, prompt=prompt)
            sql_generation = SQLGeneration(**response.json())

            self.repo.update_prompt_dh_metadata(
                prompt_id,
                DHPromptMetadata(
                    updated_by=(
                        self.user_service.get_user(user.id, org_id).name
                        if user
                        else None
                    ),
                    generation_status=(
                        GenerationStatus.NOT_VERIFIED
                        if sql_generation.status == SQLGenerationStatus.VALID
                        else GenerationStatus.ERROR
                    ),
                ),
            )
            prompt = self.repo.get_prompt(prompt_id, org_id)

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

            self._track_sql_generation_created_event(
                org_id, sql_generation, source=GenerationSource.QUERY_EDITOR_RUN
            )

            return self._get_mapped_generation_response(
                prompt, sql_generation, None, sql_result=sql_result
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
            return {"success": False}

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

        SlackWebClient(
            organization.slack_config.slack_installation.bot.token
        ).send_message(
            prompt.metadata.dh_internal.slack_info.channel_id,
            prompt.metadata.dh_internal.slack_info.thread_ts,
            message,
        )

        self.repo.update_prompt_dh_metadata(
            prompt_id,
            DHPromptMetadata(
                slack_message_last_sent_at=datetime.now(),
            ),
        )

        return {"success": True}

    async def export_csv_file(self, prompt_id: str, org_id: str) -> StreamingResponse:
        if not self.repo.get_prompt(prompt_id, org_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
            )
        sql_generation = self.repo.get_latest_sql_generation(prompt_id, org_id)
        if not sql_generation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SQL Generation not found",
            )
        if sql_generation.status != SQLGenerationStatus.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SQL Generation is not valid",
            )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.engine_url + f"/sql-generations/{sql_generation.id}/csv-file",
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)
            return StreamingResponse(
                content=response.iter_bytes(),
                headers=response.headers,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "text/csv"),
            )

    def _track_sql_generation_created_event(
        self, org_id: str, sql_generation: SQLGeneration, source: GenerationSource
    ):
        self.analytics.track(
            org_id,
            EventName.sql_generation_created,
            EventType.sql_generation_event(
                id=sql_generation.id,
                organization_id=org_id,
                source=source,
                status=sql_generation.status,
                confidence_score=sql_generation.confidence_score,
                execution_time=(
                    sql_generation.completed_at - sql_generation.created_at
                ).total_seconds(),
            ),
        )

    def _get_mapped_generation_response(
        self,
        prompt: Prompt,
        sql_generation: SQLGeneration | None,
        nl_generation: NLGeneration | None,
        sql_result: list[dict] | None = None,
    ) -> GenerationResponse:
        db_connection = self.db_connection_service.get_db_connection_in_org(
            prompt.db_connection_id, prompt.metadata.dh_internal.organization_id
        )
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

        if sql_result:
            columns = list(sql_result[0].keys()) if len(sql_result) > 0 else []
            sql_result = {"columns": columns, "rows": sql_result}

        return GenerationResponse(
            id=prompt.id,
            db_connection_id=db_connection.id,
            db_connection_alias=db_connection.alias,
            status=prompt.metadata.dh_internal.generation_status,
            prompt_text=prompt.text,
            nl_generation_text=nl_generation.text,
            sql=sql_generation.sql,
            confidence_score=sql_generation.confidence_score,
            sql_generation_error=sql_generation.error,
            created_at=prompt.created_at,
            updated_at=nl_generation.created_at or sql_generation.created_at,
            sql_result=sql_result,
            **prompt.metadata.dh_internal.dict(exclude_unset=True),
        )

    def _raise_for_generation_status(
        self, response: httpx.Response, prompt: Prompt = None, display_id: str = None
    ):
        response_json = response.json()
        if response.status_code != status.HTTP_201_CREATED:
            if prompt or ("prompt_id" in response_json and response_json["prompt_id"]):
                prompt_id = prompt.id if prompt else response_json["prompt_id"]
                self.repo.update_prompt_dh_metadata(
                    prompt_id,
                    DHPromptMetadata(
                        generation_status=GenerationStatus.ERROR,
                    ),
                )
                raise GenerationEngineError(
                    status_code=response.status_code,
                    prompt_id=prompt_id,
                    display_id=(
                        display_id or prompt.metadata.dh_internal.display_id
                        if prompt
                        else None
                    ),
                    error_message=response_json["message"],
                )
            raise_for_status(response.status_code, response.text)
