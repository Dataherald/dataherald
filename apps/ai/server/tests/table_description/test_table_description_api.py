from datetime import datetime
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from app import app
from modules.db_connection.models.entities import DBConnection
from modules.organization.models.entities import Organization
from modules.table_description.models.entities import SchemaStatus, TableDescription
from modules.user.models.entities import User

client = TestClient(app)


@patch("utils.auth.VerifyToken.verify", Mock(return_value={"email": ""}))
@patch(
    "utils.auth.Authorize.user",
    Mock(
        return_value=User(
            id="123",
            email="test@gmail.com",
            username="test_user",
            organization_id="0123456789ab0123456789ab",
        )
    ),
)
@patch(
    "modules.db_connection.service.DBConnectionService.get_db_connection",
    Mock(return_value=DBConnection(id="0123456789ab0123456789ab", alias="test_alias")),
)
@patch(
    "modules.organization.service.OrganizationService.get_organization",
    Mock(return_value=Organization(id="666f6f2d6261722d71757578")),
)
class TestTableDescriptionAPI(TestCase):
    url = "/table-descriptions"
    test_header = {"Authorization": "Bearer some-token"}
    test_1 = {
        "_id": ObjectId(b"foo-bar-quux"),
        "db_connection_id": "666f6f2d6261722d71757578",
        "table_name": "test_table",
        "description": "test_description",
        "columns": [
            {
                "categories": None,
                "data_type": None,
                "description": "test_description",
                "forengin_key": None,
                "is_primary_key": None,
                "low_cardinality": None,
                "name": "column1",
            }
        ],
        "examples": ["example1"],
        "last_schema_sync": None,
        "status": SchemaStatus.NOT_SYNCHRONIZED.value,
        "created_at": datetime.now(),
    }

    test_response_0 = {
        "id": str(test_1["_id"]),
        "table_name": test_1["table_name"],
        "db_connection_id": test_1["db_connection_id"],
        "description": test_1["description"],
        "columns": test_1["columns"],
        "examples": test_1["examples"],
        "last_schema_sync": None,
        "status": SchemaStatus.NOT_SYNCHRONIZED.value,
        "created_at": test_1["created_at"].strftime("%Y-%m-%dT%H:%M:%S.%f"),
    }

    test_response_1 = test_response_0.copy()

    test_db_response_1 = {
        "alias": "test_alias",
        "tables": [
            {
                "id": "666f6f2d6261722d71757578",
                "name": "test_table",
                "columns": ["column1"],
                "last_sync": None,
                "sync_status": SchemaStatus.NOT_SYNCHRONIZED.value,
            }
        ],
        "db_connection_id": "0123456789ab0123456789ab",
    }

    @patch(
        "modules.table_description.repository.TableDescriptionRepository.get_table_descriptions",
        Mock(return_value=[TableDescription(id=str(test_1["_id"]), **test_1)]),
    )
    def test_get_table_descriptions(self):
        response = client.get(self.url, headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [self.test_response_0]

    @patch("database.mongo.MongoDB.find_by_id", Mock(return_value=test_1))
    def test_get_table_description(self):
        response = client.get(
            self.url + "/666f6f2d6261722d71757578", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1

    @patch(
        "modules.table_description.repository.TableDescriptionRepository.get_table_descriptions",
        Mock(return_value=[TableDescription(id=str(test_1["_id"]), **test_1)]),
    )
    def test_get_database_table_descriptions(self):
        response = client.get(self.url + "/database/list", headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [self.test_db_response_1]

    @patch(
        "modules.table_description.service.TableDescriptionService.sync_table_descriptions_schemas",
        AsyncMock(return_value=True),
    )
    def test_sync_table_descriptions_schemas(self):
        response = client.post(
            self.url + "/sync-schemas",
            headers=self.test_header,
            json={
                "db_connection_id": "0123456789ab0123456789ab",
                "table_names": ["test_table"],
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    @patch(
        "httpx.AsyncClient.patch",
        AsyncMock(return_value=Response(status_code=200, json=test_response_1)),
    )
    @patch("database.mongo.MongoDB.find_by_id", Mock(return_value=test_1))
    def test_update_table_description(self):
        response = client.patch(
            self.url + "/666f6f2d6261722d71757578",
            headers=self.test_header,
            json={
                "description": "test_description",
                "columns": [{"name": "column1", "description": "test_description"}],
                "examples": ["example1"],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1
