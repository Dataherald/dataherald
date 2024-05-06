from bson import ObjectId

from config import DATABASE_CONNECTION_COL, ORGANIZATION_COL
from database.mongo import MongoDB
from modules.organization.models.entities import Organization


class OrganizationRepository:
    def get_organizations(self) -> list[Organization]:
        return [
            Organization(id=str(organization["_id"]), **organization)
            for organization in MongoDB.find(ORGANIZATION_COL, {}).sort("name")
        ]

    def get_organization(self, org_id: str) -> Organization:
        organization = MongoDB.find_by_id(ORGANIZATION_COL, org_id)
        return (
            Organization(id=str(organization["_id"]), **organization)
            if organization
            else None
        )

    def get_organization_by_slack_workspace_id(
        self, slack_workspace_id: str
    ) -> Organization:
        organization = MongoDB.find_one(
            ORGANIZATION_COL,
            {"slack_config.slack_installation.team.id": slack_workspace_id},
        )
        return (
            Organization(id=str(organization["_id"]), **organization)
            if organization
            else None
        )

    def get_organization_by_customer_id(self, customer_id: str) -> Organization:
        organization = MongoDB.find_one(
            ORGANIZATION_COL,
            {"invoice_details.stripe_customer_id": customer_id},
        )
        return (
            Organization(id=str(organization["_id"]), **organization)
            if organization
            else None
        )

    def delete_organization(self, org_id: str) -> int:
        return MongoDB.delete_one(ORGANIZATION_COL, {"_id": ObjectId(org_id)})

    def update_organization(self, org_id: str, new_org_data: dict) -> int:
        return MongoDB.update_one(
            ORGANIZATION_COL, {"_id": ObjectId(org_id)}, new_org_data
        )

    def add_organization(self, new_org_data: Organization) -> str:
        return str(
            MongoDB.insert_one(ORGANIZATION_COL, new_org_data.dict(exclude={"id"}))
        )

    # TODO: should be implemented in the db_connection module
    def insert_or_replace_llm_api_key(self, org_id: str, api_key: str) -> int:
        # note that enterprise and engine must have the same encryption key
        return MongoDB.update_one(
            DATABASE_CONNECTION_COL,
            {"metadata.dh_internal.organization_id": org_id},
            {"llm_api_key": api_key},
        )
