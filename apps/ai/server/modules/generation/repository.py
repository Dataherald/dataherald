from bson import ObjectId

from config import (
    NL_GENERATION_COL,
    PROMPT_COL,
    SQL_GENERATION_COL,
)
from database.mongo import ASCENDING, DESCENDING, MongoDB
from modules.generation.models.entities import (
    DHPromptMetadata,
    NLGeneration,
    Prompt,
    SQLGeneration,
)
from utils.misc import get_next_display_id


class GenerationRepository:
    def get_prompt(self, prompt_id: str, org_id: str) -> Prompt:
        prompt = MongoDB.find_one(
            PROMPT_COL,
            {
                "_id": ObjectId(prompt_id),
                "metadata.dh_internal.organization_id": org_id,
            },
        )
        return Prompt(id=str(prompt["_id"]), **prompt) if prompt else None

    def get_prompts(
        self, skip: int, limit: int, order: str, ascend: bool, org_id: str
    ) -> list[Prompt]:
        prompts = self._get_items(
            skip,
            limit,
            order,
            ascend,
            PROMPT_COL,
            {"metadata.dh_internal.organization_id": org_id},
        )
        return [Prompt(id=str(prompt["_id"]), **prompt) for prompt in prompts]

    def get_sql_generation(
        self, sql_generation_id: str, org_id: str = None
    ) -> SQLGeneration:
        sql_generation = MongoDB.find_one(
            SQL_GENERATION_COL,
            {
                "_id": ObjectId(sql_generation_id),
                "metadata.dh_internal.organization_id": org_id,
            },
        )
        return (
            SQLGeneration(id=str(sql_generation["_id"]), **sql_generation)
            if sql_generation
            else None
        )

    def get_latest_sql_generation(self, prompt_id: str, org_id: str) -> SQLGeneration:
        sql_generation = self._get_latest_item(
            SQL_GENERATION_COL,
            {
                "prompt_id": prompt_id,
                "metadata.dh_internal.organization_id": org_id,
            },
        )
        return (
            SQLGeneration(id=str(sql_generation["_id"]), **sql_generation)
            if sql_generation
            else None
        )

    def get_sql_generations(
        self,
        skip: int,
        limit: int,
        order: str,
        ascend: bool,
        org_id: str,
        prompt_id: str = None,
    ):
        query = {"metadata.dh_internal.organization_id": org_id}
        if prompt_id:
            query["prompt_id"] = prompt_id
        sql_generations = self._get_items(
            skip, limit, order, ascend, SQL_GENERATION_COL, query
        )
        return [
            SQLGeneration(id=str(sql_generation["_id"]), **sql_generation)
            for sql_generation in sql_generations
        ]

    def get_nl_generation(self, nl_generation_id: str, org_id: str) -> NLGeneration:
        nl_generation = MongoDB.find_one(
            NL_GENERATION_COL,
            {
                "_id": ObjectId(nl_generation_id),
                "metadata.dh_internal.organization_id": org_id,
            },
        )
        return (
            NLGeneration(id=str(nl_generation["_id"]), **nl_generation)
            if nl_generation
            else None
        )

    def get_latest_nl_generation(
        self, sql_generation_id: str, org_id: str
    ) -> NLGeneration:
        nl_generation = self._get_latest_item(
            NL_GENERATION_COL,
            {
                "sql_generation_id": sql_generation_id,
                "metadata.dh_internal.organization_id": org_id,
            },
        )
        return (
            NLGeneration(id=str(nl_generation["_id"]), **nl_generation)
            if nl_generation
            else None
        )

    def get_nl_generations(
        self,
        skip: int,
        limit: int,
        order: str,
        ascend: bool,
        org_id: str,
        sql_generation_id: str = None,
    ):
        query = {"metadata.dh_internal.organization_id": org_id}
        if sql_generation_id:
            query["sql_generation_id"] = sql_generation_id
        nl_generations = self._get_items(
            skip, limit, order, ascend, NL_GENERATION_COL, query
        )
        return [
            NLGeneration(id=str(nl_generation["_id"]), **nl_generation)
            for nl_generation in nl_generations
        ]

    def get_next_display_id(self, org_id: str) -> str:
        return get_next_display_id(PROMPT_COL, org_id, "QR")

    def update_prompt_dh_metadata(
        self, prompt_id: str, metadata: DHPromptMetadata
    ) -> int:
        new_metadata = {}
        for key, value in metadata.dict(exclude_unset=True).items():
            new_key = "metadata.dh_internal." + key
            new_metadata[new_key] = value
        return MongoDB.update_one(
            PROMPT_COL,
            {"_id": ObjectId(prompt_id)},
            new_metadata,
        )

    def _get_items(
        self,
        skip: int,
        limit: int,
        order: str,
        ascend: bool,
        item_col: str,
        query: dict,
    ):
        return (
            MongoDB.find(item_col, query)
            .sort([(order, ASCENDING if ascend else DESCENDING)])
            .skip(skip)
            .limit(limit)
        )

    def _get_latest_item(self, item_col: str, query: dict):
        return MongoDB.find_one(item_col, query, sort=[("created_at", DESCENDING)])
