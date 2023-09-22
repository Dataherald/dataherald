from unittest import TestCase
from unittest.mock import Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


@patch("utils.auth.VerifyToken.verify", Mock(return_value={"email": ""}))
@patch("utils.auth.Authorize.is_root_user", Mock(return_value=None))
class TestOrganizationAPI(TestCase):
    url = "/organization"
    test_header = {"Authorization": "Bearer some-token"}

    test_1 = {
        "_id": ObjectId(b"foo-bar-quux"),
        "name": "test_org_1",
        "confidence_threshold": 0.5,
        "db_connection_id": "test_connection_id_1",
        "llm_credentials": None,
    }

    test_2 = {
        "_id": ObjectId(b"lao-gan-maaa"),
        "name": "test_org_2",
        "confidence_threshold": 1.0,
        "db_connection_id": "test_connection_id_2",
        "slack_installation": {
            "team": {
                "id": "0123456789ab0123456789ab",
                "name": "test_1",
            },
            "enterprise": None,
            "user": {
                "id": "0123456789ab0123456789ab",
                "scopes": None,
                "token": "test_token",
            },
            "bot": {
                "scopes": [],
                "id": "0123456789ab0123456789ab",
                "token": "test_token",
                "user_id": "0123456789ab0123456789ab",
            },
            "token_type": "test_1",
            "is_enterprise_install": False,
            "auth_version": "V2",
            "app_id": "0123456789ab0123456789ab",
        },
        "llm_credentials": None,
    }

    test_response_1 = {
        "id": str(test_1["_id"]),
        "name": test_1["name"],
        "db_connection_id": test_1["db_connection_id"],
        "confidence_threshold": test_1["confidence_threshold"],
        "slack_installation": None,
        "llm_credentials": None,
    }

    test_response_2 = {
        "id": str(test_2["_id"]),
        "name": test_2["name"],
        "db_connection_id": test_2["db_connection_id"],
        "confidence_threshold": test_2["confidence_threshold"],
        "slack_installation": test_2["slack_installation"],
        "llm_credentials": None,
    }

    @patch("database.mongo.MongoDB.find", Mock(return_value=[test_1, test_2]))
    def test_get_organizations(self):
        response = client.get(self.url + "/list", headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [self.test_response_1, self.test_response_2]

    @patch("database.mongo.MongoDB.find_by_id", Mock(return_value=test_1))
    def test_get_organization(self):
        response = client.get(
            self.url + "/0123456789ab0123456789ab", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1

    @patch.multiple(
        "database.mongo.MongoDB",
        find_by_id=Mock(return_value=test_1),
        find_one=Mock(return_value=None),
        insert_one=Mock(return_value=str(test_1)),
    )
    def test_add_organization(self):
        response = client.post(
            self.url,
            headers=self.test_header,
            json={"name": "test_1", "db_connection_id": "0123456789ab0123456789ab"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == self.test_response_1

    @patch.multiple(
        "database.mongo.MongoDB",
        find_by_id=Mock(return_value=test_1),
        update_one=Mock(return_value=1),
    )
    def test_update_organization(self):
        response = client.put(
            self.url + "/0123456789ab0123456789ab",
            headers=self.test_header,
            json={"name": "test_1", "db_connection_id": "0123456789ab0123456789ab"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1

    @patch(
        "database.mongo.MongoDB.delete_one",
        Mock(return_value=1),
    )
    def test_delete(self):
        response = client.delete(
            self.url + "/0123456789ab0123456789ab", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": "0123456789ab0123456789ab"}

    @patch.multiple(
        "database.mongo.MongoDB",
        find_by_id=Mock(return_value=test_1),
        find_one=Mock(return_value=None),
        insert_one=Mock(return_value=str(test_1)),
    )
    def test_add_organization_by_slack_installation(self):
        response = client.post(
            self.url + "/slack/installation",
            headers=self.test_header,
            json={
                "team": {
                    "id": "0123456789ab0123456789ab",
                    "name": "test_1",
                },
                "enterprise": None,
                "user": {
                    "id": "0123456789ab0123456789ab",
                    "scopes": None,
                    "token": "test_token",
                },
                "bot": {
                    "scopes": [],
                    "id": "0123456789ab0123456789ab",
                    "token": "test_token",
                    "userId": "0123456789ab0123456789ab",
                },
                "tokenType": "test_1",
                "isEnterpriseInstall": False,
                "authVersion": "V2",
                "appId": "0123456789ab0123456789ab",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == self.test_response_1

    @patch("database.mongo.MongoDB.find_one", Mock(return_value=test_response_2))
    def test_get_slack_installation_by_slack_workspace_id(self):
        response = client.get(
            self.url + "/slack/installation?workspace_id=0123456789ab0123456789ab",
            headers=self.test_header,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_2["slack_installation"]
