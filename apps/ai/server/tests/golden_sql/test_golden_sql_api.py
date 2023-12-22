from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch

from bson import ObjectId
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

    # @patch(
    #     "modules.golden_sql.repository.GoldenSQLRepository.get_golden_sqls",
    #     Mock(
    #     ),
    # def test_get_golden_sqls(self):

    # @patch("database.mongo.MongoDB.find_one", Mock(return_value=test_1))
    # def test_get_golden_sql(self):

    # @patch(
    #     "httpx.AsyncClient.post",
    # @patch(
    #     "modules.golden_sql.repository.GoldenSQLRepository.get_next_display_id",
    # def test_add_golden_sql(self):
    #         self.url + "/user-upload",
    #         ],

    # @patch(
    #     "httpx.AsyncClient.delete",
    # @patch.multiple(
    #     "modules.golden_sql.repository.GoldenSQLRepository",
    # def test_delete_golden_sql(self):
