from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from app import app
from modules.db_connection.models.responses import DBConnectionResponse
from modules.organization.models.entities import Organization
from modules.table_description.models.entities import SchemaStatus
from modules.user.models.responses import UserResponse

client = TestClient(app)


@patch("utils.auth.VerifyToken.verify", Mock(return_value={"email": ""}))
@patch.multiple(
    "utils.auth.Authorize",
    user=Mock(
        return_value=UserResponse(
            id="123",
            email="test@gmail.com",
            username="test_user",
            organization_id="0123456789ab0123456789ab",
        )
    ),
    get_organization_by_user_response=Mock(
        return_value=Organization(
            id="123", name="test_org", db_connection_id="0123456789ab0123456789ab"
        )
    ),
    table_description_in_organization=Mock(return_value=None),
)
class TestTableDescriptionAPI(TestCase):
    url = "/table-description"
    test_header = {"Authorization": "Bearer some-token"}
    test_1 = {
        "id": ObjectId(b"foo-bar-quux"),
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
    }

    test_response_0 = {
        "id": str(test_1["id"]),
        "table_name": test_1["table_name"],
        "description": test_1["description"],
        "columns": test_1["columns"],
        "examples": test_1["examples"],
        "last_schema_sync": None,
        "status": SchemaStatus.NOT_SYNCHRONIZED.value,
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
        "instructions": "",
    }

    @patch(
        "httpx.AsyncClient.get",
        AsyncMock(return_value=Response(status_code=200, json=[test_response_0])),
    )
    def test_get_table_descriptions(self):
        response = client.get(self.url + "/list", headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [self.test_response_0]

    @patch(
        "httpx.AsyncClient.get",
        AsyncMock(return_value=Response(status_code=200, json=test_response_0)),
    )
    def test_get_table_description(self):
        response = client.get(
            self.url + "/666f6f2d6261722d71757578", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_0

    @patch(
        "httpx.AsyncClient.get",
        AsyncMock(return_value=Response(status_code=200, json=[test_response_0])),
    )
    @patch(
        "modules.instruction.service.InstructionService.get_instructions",
        AsyncMock(return_value=[]),
    )
    @patch(
        "modules.db_connection.service.DBConnectionService.get_db_connection",
        Mock(
            return_value=DBConnectionResponse(
                id="0123456789ab0123456789ab",
                alias=test_db_response_1["alias"],
                uri="test_uri",
            )
        ),
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
        AsyncMock(return_value=Response(status_code=200, json=test_response_0)),
    )
    def test_update_table_description(self):
        response = client.patch(
            self.url + "/123",
            headers=self.test_header,
            json={
                "description": "test_description",
                "columns": [{"name": "column1", "description": "test_description"}],
                "examples": ["example1"],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1
