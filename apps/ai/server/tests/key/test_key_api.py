from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient

from app import app
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
class TestKeyAPI(TestCase):
    url = "/keys"
    test_header = {"Authorization": "Bearer some-token"}
    test_1 = {
        "_id": ObjectId(b"foo-bar-quux"),
        "name": "test_key",
        "organization_id": "0123456789ab0123456789ab",
        "key_preview": "dh-························fbf",
        "key_hash": b"btfGQsNhfySbJJ2njoA0sT/CY7MZ1gI/IQ0QMQq9G6A=",
        "created_at": datetime.now(),
    }

    test_preview_response_1 = {
        "id": str(test_1["_id"]),
        "name": test_1["name"],
        "organization_id": "0123456789ab0123456789ab",
        "key_preview": test_1["key_preview"],
        "created_at": test_1["created_at"].strftime("%Y-%m-%dT%H:%M:%S.%f"),
    }

    test_response_1 = {
        **test_preview_response_1,
        "api_key": "dh-be7e6482b83bc99e7589c1f8e9ed3b047d662b5ad3a84a3bb08a5dead91c3fbf",
    }

    @patch("database.mongo.MongoDB.find", Mock(return_value=[test_1]))
    def test_get_keys(self):
        response = client.get(self.url, headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [self.test_preview_response_1]

    @patch.multiple(
        "database.mongo.MongoDB",
        find_one=Mock(return_value=None),
        insert_one=Mock(return_value="666f6f2d6261722d71757578"),
    )
    def test_add_key(self):
        response = client.post(
            self.url, headers=self.test_header, json={"name": "test_key"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        response_json = response.json()
        assert response_json["name"] == self.test_response_1["name"]
        assert (
            response_json["organization_id"] == self.test_response_1["organization_id"]
        )

    @patch("database.mongo.MongoDB.delete_one", Mock(return_value=1))
    def test_revoke_key(self):
        response = client.delete(
            self.url + "/666f6f2d6261722d71757578", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": "666f6f2d6261722d71757578"}
