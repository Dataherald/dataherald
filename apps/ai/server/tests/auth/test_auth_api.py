from unittest import TestCase
from unittest.mock import Mock, patch

from fastapi import status
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


@patch("utils.auth.VerifyToken.verify", Mock(return_value={"email": ""}))
class TestAuthAPI(TestCase):
    url = "/auth"
    test_header = {"Authorization": "Bearer some-token"}

    @patch(
        "modules.auth.service.AuthService.login",
        Mock(
            return_value={
                "id": "test_id",
                "email": "test@gmail.com",
                "name": "test_name",
                "organization_id": "test_org_id",
                "organization_name": "test_org",
            }
        ),
    )
    def test_login(self):
        response = client.post(
            self.url + "/login",
            headers=self.test_header,
            json={
                "email": "test@gmail.com",
                "name": "test_name",
            },
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
