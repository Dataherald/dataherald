"""
from datetime import datetime
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from app import app
from modules.db_connection.models.entities import DBConnection
from modules.finetuning.models.entities import FineTuningStatus
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
    Mock(return_value=DBConnection(id="123", alias="test_alias", connection_uri="foo://bar/K2")),
)
class TestFinetuningAPI(TestCase):
    url = "/finetunings"
    test_header = {"Authorization": "Bearer some-token"}
    test_1 = {
        "_id": ObjectId(b"foo-bar-quux"),
        "db_connection_id": "0123456789ab0123456789ab",
        "status": FineTuningStatus.QUEUED,
        "base_llm": {
            "model_provider": "huggingface",
            "model_name": "test_model",
            "model_parameters": {"test_parameter": "test_value"},
        },
        "metadata": {"organization_id": "0123456789ab0123456789ab"},
        "created_at": datetime.now(),
    }

    test_response_1 = {
        "id": str(test_1["_id"]),
        "db_connection_id": test_1["db_connection_id"],
        "status": test_1["status"],
        "base_llm": test_1["base_llm"],
        "created_at": test_1["created_at"].strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "golden_records": None,
        "error": None,
        "finetuning_file_id": None,
        "finetuning_job_id": None,
        "model_id": None,
        "metadata": {"organization_id": "0123456789ab0123456789ab"},
    }

    @patch("database.mongo.MongoDB.find_one", Mock(return_value=test_1))
    def test_get_finetuning_job(self):
        response = client.get(
            self.url + "/666f6f2d6261722d71757578", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1

    @patch(
        "httpx.AsyncClient.post",
        AsyncMock(return_value=Response(status_code=201, json=test_response_1)),
    )
    def test_create_finetuning_job(self):
        response = client.post(
            self.url,
            headers=self.test_header,
            json={
                "db_connection_id": "0123456789ab0123456789ab",
                "base_llm": {
                    "model_provider": "huggingface",
                    "model_name": "test_model",
                    "model_parameters": {"test_parameter": "test_value"},
                },
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == self.test_response_1

    @patch(
        "httpx.AsyncClient.post",
        AsyncMock(return_value=Response(status_code=200, json=test_response_1)),
    )
    @patch("database.mongo.MongoDB.find_one", Mock(return_value=test_1))
    def test_cancel_finetuning_job(self):
        response = client.post(
            self.url + "/666f6f2d6261722d71757578/cancel", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1
"""
