import json
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from app import app
from modules.user.models.entities import User

client = TestClient(app)


@patch("utils.auth.VerifyToken.verify", Mock(return_value={"email": ""}))
@patch(
    "utils.auth.Authorize.user",
    Mock(
        return_value=User(
            id="0123456789ab0123456789ab",
            email="test@gmail.com",
            username="test_user",
            organization_id="0123456789ab0123456789ab",
        )
    ),
)
class TestDBConnectionAPI(TestCase):
    url = "/database-connections"
    test_header = {"Authorization": "Bearer some-token"}
    test_1 = {
        "_id": ObjectId(b"foo-bar-quux"),
        "alias": "test_connection_1",
        "use_ssh": False,
        "uri": "test_uri_1",
        "path_to_credentials_file": None,
        "llm_api_key": None,
        "metadata": {
            "organization_id": "0123456789ab0123456789ab",
        },
    }
    test_2 = {
        "_id": ObjectId(b"lao-gan-maaa"),
        "alias": "test_connection_2",
        "use_ssh": False,
        "uri": "test_uri_2",
        "path_to_credentials_file": None,
        "llm_api_key": None,
        "metadata": {
            "organization_id": "0123456789ab0123456789ab",
        },
    }

    test_response_1 = {
        "id": str(test_1["_id"]),
        "alias": test_1["alias"],
        "use_ssh": test_1["use_ssh"],
        "uri": test_1["uri"],
        "path_to_credentials_file": test_1["path_to_credentials_file"],
        "ssh_settings": None,
        "llm_api_key": None,
        "metadata": {
            "organization_id": "0123456789ab0123456789ab",
        },
    }

    test_response_2 = {
        "id": str(test_2["_id"]),
        "alias": test_2["alias"],
        "use_ssh": test_2["use_ssh"],
        "uri": test_2["uri"],
        "path_to_credentials_file": test_2["path_to_credentials_file"],
        "ssh_settings": None,
        "llm_api_key": None,
        "metadata": {
            "organization_id": "0123456789ab0123456789ab",
        },
    }

    @patch("database.mongo.MongoDB.find", Mock(return_value=[test_1, test_2]))
    def test_get_db_connections(self):
        response = client.get(self.url, headers=self.test_header)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            self.test_response_1,
            self.test_response_2,
        ]

    @patch("database.mongo.MongoDB.find_one", Mock(return_value=test_1))
    def test_get_db_connection(self):
        response = client.get(
            self.url + "/0123456789ab0123456789ab", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1

    @patch(
        "httpx.AsyncClient.post",
        AsyncMock(return_value=Response(status_code=201, json=test_response_1)),
    )
    @patch(
        "modules.organization.service.OrganizationService.update_db_connection_id",
        Mock(return_value=None),
    )
    def test_add_db_connection(self):
        data = {
            "db_connection_request_json": json.dumps(
                {
                    "alias": "test_connection",
                    "use_ssh": False,
                    "connection_uri": "test_uri",
                }
            )
        }
        response = client.post(
            self.url,
            headers=self.test_header,
            data=data,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == self.test_response_1

    @patch(
        "httpx.AsyncClient.put",
        AsyncMock(return_value=Response(status_code=200, json=test_response_1)),
    )
    @patch(
        "modules.db_connection.repository.DBConnectionRepository.get_db_connection",
        Mock(return_value=test_1),
    )
    def test_update_db_connection(self):
        data = {
            "db_connection_request_json": json.dumps(
                {
                    "alias": "test_connection",
                    "use_ssh": False,
                    "connection_uri": "test_uri",
                }
            )
        }
        response = client.put(
            self.url + "/0123456789ab0123456789ab",
            headers=self.test_header,
            data=data,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1
