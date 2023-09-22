from unittest import TestCase
from unittest.mock import Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


@patch("utils.auth.VerifyToken.verify", Mock(return_value={"email": ""}))
@patch.multiple(
    "utils.auth.Authorize",
    user_and_get_org_id=Mock(return_value=str(ObjectId(b"lao-gan-maaa"))),
    user_in_organization=Mock(return_value=None),
)
class TestUserAPI(TestCase):
    url = "/user"
    test_header = {"Authorization": "Bearer some-token"}
    test_1 = {
        "_id": ObjectId(b"foo-bar-quux"),
        "email": "test@gmail.com",
        "organization_id": ObjectId(b"lao-gan-maaa"),
        "email_verified": True,
        "name": "test",
        "nickname": "test",
        "picture": "test",
        "sub": "test",
        "updated_at": "test",
    }

    test_response_1 = {
        "id": str(test_1["_id"]),
        "email": "test@gmail.com",
        "organization_id": str(test_1["organization_id"]),
        "email_verified": True,
        "name": "test",
        "nickname": "test",
        "picture": "test",
        "sub": "test",
        "updated_at": "test",
    }

    @patch("database.mongo.MongoDB.find", Mock(return_value=[test_1]))
    def test_get_users(self):
        response = client.get(self.url + "/list", headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [self.test_response_1]

    @patch("database.mongo.MongoDB.find_by_id", Mock(return_value=test_1))
    def test_get_user(self):
        response = client.get(
            self.url + "/666f6f2d6261722d71757578", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1

    @patch.multiple(
        "database.mongo.MongoDB",
        find_one=Mock(return_value=None),
        insert_one=Mock(return_value=test_1["_id"]),
        find_by_id=Mock(return_value=test_1),
    )
    def test_add_user(self):
        response = client.post(
            self.url,
            headers=self.test_header,
            json={"name": "test", "email": "test@gmail.com"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == self.test_response_1

    @patch.multiple(
        "database.mongo.MongoDB",
        update_one=Mock(return_value=1),
        find_by_id=Mock(return_value=test_1),
    )
    def test_update_user(self):
        response = client.put(
            self.url + "/666f6f2d6261722d71757578",
            headers=self.test_header,
            json={"name": "test", "email": "test@gmail.com"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1

    @patch(
        "modules.user.service.UserService.delete_user", Mock(return_value={"id": "123"})
    )
    def test_delete_user(self):
        response = client.delete(
            self.url + "/666f6f2d6261722d71757578", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
