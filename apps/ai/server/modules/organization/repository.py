from bson import ObjectId

from config import (
    DATABASE_CONNECTION_COL,
    DATABASE_CONNECTION_REF_COL,
    ORGANIZATION_COL,
)
from database.mongo import MongoDB
from modules.organization.models.entities import Organization


class OrganizationRepository:
    def get_organizations(self) -> list[Organization]:
        return [
            Organization(**organization)
            for organization in MongoDB.find(ORGANIZATION_COL, {})
        ]

    def get_organization(self, org_id: str) -> Organization:
        organization = MongoDB.find_by_id(ORGANIZATION_COL, org_id)
        return Organization(**organization) if organization else None

    def get_organization_by_slack_workspace_id(
        self, slack_workspace_id: str
    ) -> Organization:
        organization = MongoDB.find_one(
            ORGANIZATION_COL, {"slack_installation.team.id": slack_workspace_id}
        )
        return Organization(**organization) if organization else None

    def delete_organization(self, org_id: str) -> int:
        return MongoDB.delete_one(ORGANIZATION_COL, {"_id": ObjectId(org_id)})

    def update_organization(self, org_id: str, new_org_data: dict) -> int:
        return MongoDB.update_one(
            ORGANIZATION_COL, {"_id": ObjectId(org_id)}, new_org_data
        )

    def add_organization(self, new_org_data: dict) -> str:
        # each organization should have unique name
        if MongoDB.find_one(ORGANIZATION_COL, {"name": new_org_data["name"]}):
            return None
        return str(MongoDB.insert_one(ORGANIZATION_COL, new_org_data))

    # this violates the architecture, but it's a quick fix for now
    # TODO: need to avoid cross resource dependency and avoid circular dependency
    def update_db_connections_llm_api_key(self, org_id: str, llm_api_key: str) -> int:
        cursor = MongoDB.find(
            DATABASE_CONNECTION_REF_COL, {"organization_id": ObjectId(org_id)}
        )
        count = 0
        for ref in cursor:
            count += MongoDB.update_one(
                DATABASE_CONNECTION_COL,
                {"_id": ref["db_connection_id"]},
                {"llm_api_key": llm_api_key},
            )

        return count
