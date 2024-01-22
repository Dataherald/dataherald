from datetime import datetime
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient

from app import app
from modules.db_connection.models.entities import DBConnection
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
    Mock(
        return_value=DBConnection(
            id="123", alias="test_alias", connection_uri="foo://bar/K2"
        )
    ),
)
class TestInstructionAPI(TestCase):
    url = "/instructions"
    test_header = {"Authorization": "Bearer some-token"}
    test_1 = {
        "_id": ObjectId(b"foo-bar-quux"),
        "instruction": "test_instruction",
        "db_connection_id": "0123456789ab0123456789ab",
        "created_at": datetime.now(),
    }

    test_response_0 = {
        "id": str(test_1["_id"]),
        "instruction": "test_instruction",
        "db_connection_id": "0123456789ab0123456789ab",
        "created_at": test_1["created_at"].strftime("%Y-%m-%dT%H:%M:%S.%f"),
    }

    test_response_1 = test_response_0.copy()

    # @patch(
    #     "modules.instruction.repository.InstructionRepository.get_instructions",
    # def test_get_instructions(self):
    #         self.url,

    # @patch(
    #     "modules.instruction.repository.InstructionRepository.get_instructions",
    # @patch(
    #     "modules.organization.service.OrganizationService.get_organization",
    # def test_get_first_instruction(self):

    # @patch(
    #     "httpx.AsyncClient.post",
    # def test_add_instruction(self):
    #         self.url,
    #         },

    # @patch(
    #     "httpx.AsyncClient.put",
    # def test_update_instruction(self):
    #         self.url + "/666f6f2d6261722d71757578",
    #         },

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
