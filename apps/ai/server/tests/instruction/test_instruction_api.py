from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from app import app
from modules.organization.models.entities import Organization
from modules.user.models.entities import User

client = TestClient(app)


@patch("utils.auth.VerifyToken.verify", Mock(return_value={"email": ""}))
@patch.multiple(
    "utils.auth.Authorize",
    user=Mock(
        return_value=User(
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
    instruction_in_organization=Mock(return_value=None),
)
class TestInstructionAPI(TestCase):
    url = "/instruction"
    test_header = {"Authorization": "Bearer some-token"}
    test_1 = {
        "id": ObjectId(b"foo-bar-quux"),
        "instruction": "test_instruction",
        "db_connection_id": "0123456789ab0123456789ab",
    }

    test_response_0 = {
        "id": str(test_1["id"]),
        "instruction": "test_instruction",
        "db_connection_id": "0123456789ab0123456789ab",
    }

    test_response_1 = test_response_0.copy()

    @patch(
        "httpx.AsyncClient.get",
        AsyncMock(return_value=Response(status_code=200, json=[test_response_0])),
    )
    def test_get_instructions(self):
        response = client.get(self.url + "/list", headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [self.test_response_1]

    @patch(
        "httpx.AsyncClient.post",
        AsyncMock(return_value=Response(status_code=201, json=test_response_0)),
    )
    def test_add_instruction(self):
        response = client.post(
            self.url,
            headers=self.test_header,
            json={
                "instruction": "test_description",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == self.test_response_1

    @patch(
        "httpx.AsyncClient.put",
        AsyncMock(return_value=Response(status_code=200, json=test_response_0)),
    )
    def test_update_instruction(self):
        response = client.put(
            self.url + "/666f6f2d6261722d71757578",
            headers=self.test_header,
            json={
                "instruction": "test_description",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1

    @patch(
        "modules.instruction.service.InstructionService.delete_instruction",
        AsyncMock(return_value={"status": True}),
    )
    def test_delete_instruction(self):
        response = client.delete(
            self.url + "/666f6f2d6261722d71757578",
            headers=self.test_header,
        )
        assert response.status_code == status.HTTP_200_OK
