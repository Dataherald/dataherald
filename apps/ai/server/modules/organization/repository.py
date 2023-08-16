from bson import ObjectId

from config import ORGANIZATION_COL
from database.mongo import MongoDB
from modules.organization.models.entities import Organization


class OrganizationRepository:
    def list_organizations(self) -> list[Organization]:
        return [
            Organization(**organization)
            for organization in MongoDB.find(ORGANIZATION_COL, {})
        ]

    def get_organization(self, id: str) -> Organization:
        return Organization(**MongoDB.find_by_id(ORGANIZATION_COL, id))

    def delete_organization(self, id: str) -> int:
        return MongoDB.delete_one("organization", {"_id": ObjectId(id)})

    def update_organization(self, id: str, new_org_data: dict) -> int:
        return MongoDB.update_one(ORGANIZATION_COL, {"_id": ObjectId(id)}, new_org_data)

    def add_organization(self, new_org_data: dict) -> int:
        # each organization should have unique name
        if MongoDB.find_one(ORGANIZATION_COL, {"name": new_org_data["name"]}):
            return None
        return MongoDB.insert_one(ORGANIZATION_COL, new_org_data)
