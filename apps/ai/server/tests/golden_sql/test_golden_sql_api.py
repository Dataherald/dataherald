from datetime import datetime
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from app import app
from modules.golden_sql.models.entities import GoldenSQL
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
class TestGoldenSQLAPI(TestCase):
    url = "/golden-sqls"
    test_header = {"Authorization": "Bearer some-token"}

    metadata = {
        "question_id": "test_question_id",
        "organization_id": "test_org_id",
        "display_id": "GS-00001",
        "source": "VERIFIED_QUERY",
        "question_display_id": "QR-00001",
    }
    created_at = datetime.now()

    test_1 = {
        "_id": ObjectId(b"foo-bar-quux"),
        "prompt_text": "test_question",
        "sql": "test_query",
        "db_connection_id": "test_connection_id",
        "metadata": metadata,
        "created_at": created_at,
    }

    test_2 = {
        "_id": ObjectId(b"lao-gan-maaa"),
        "prompt_text": "test_question",
        "sql": "test_query",
        "db_connection_id": "test_connection_id",
        "metadata": metadata,
        "created_at": created_at,
    }

    test_response_0 = {
        "id": str(test_1["_id"]),
        "prompt_text": "test_question",
        "sql": "test_query",
        "db_connection_id": "test_connection_id",
        "metadata": metadata,
        "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
    }

    test_response_1 = {
        "id": str(test_1["_id"]),
        "prompt_text": test_1["prompt_text"],
        "sql": test_1["sql"],
        "db_connection_id": test_1["db_connection_id"],
        "metadata": metadata,
        "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
    }

    test_response_2 = {
        "id": str(test_2["_id"]),
        "prompt_text": test_2["prompt_text"],
        "sql": test_2["sql"],
        "db_connection_id": test_2["db_connection_id"],
        "metadata": metadata,
        "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
    }

    @patch(
        "modules.golden_sql.repository.GoldenSQLRepository.get_golden_sqls",
        Mock(
            return_value=[
                GoldenSQL(id=str(test_1["_id"]), **test_1),
                GoldenSQL(id=str(test_2["_id"]), **test_2),
            ]
        ),
    )
    def test_get_golden_sqls(self):
        response = client.get(self.url + "", headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [self.test_response_1, self.test_response_2]

    @patch("database.mongo.MongoDB.find_one", Mock(return_value=test_1))
    def test_get_golden_sql(self):
        response = client.get(
            self.url + "/0123456789ab0123456789ab", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1

    @patch(
        "httpx.AsyncClient.post",
        AsyncMock(return_value=Response(status_code=201, json=[test_response_0])),
    )
    @patch(
        "modules.golden_sql.repository.GoldenSQLRepository.get_next_display_id",
        Mock(return_value="GS-00001"),
    )
    def test_add_golden_sql(self):
        response = client.post(
            self.url + "/user-upload",
            headers=self.test_header,
            json=[
                {
                    "prompt_text": "test_question",
                    "sql": "test_query",
                    "db_connection_id": "test_connection_id",
                }
            ],
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == [self.test_response_1]

    @patch(
        "httpx.AsyncClient.delete",
        AsyncMock(return_value=Response(status_code=200, json={"status": True})),
    )
    @patch.multiple(
        "modules.golden_sql.repository.GoldenSQLRepository",
        get_golden_sql=Mock(return_value=GoldenSQL(id=str(test_2["_id"]), **test_2)),
        update_generation_status=Mock(return_value=None),
    )
    def test_delete_golden_sql(self):
        response = client.delete(
            self.url + "/0123456789ab0123456789ab", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
