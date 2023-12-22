from unittest import TestCase
from unittest.mock import Mock, patch

from bson import ObjectId
from fastapi.testclient import TestClient

from app import app
from modules.db_connection.models.responses import DBConnectionResponse
from modules.organization.models.responses import OrganizationResponse
from modules.user.models.entities import User

client = TestClient(app)


@patch("utils.auth.VerifyToken.verify", Mock(return_value={"email": ""}))
@patch.multiple(
    "utils.auth.Authorize",
    user=Mock(
        return_value=User(
            id="0123456789ab0123456789ab",
            email="test@gmail.com",
            username="test_user",
            organization_id="0123456789ab0123456789ab",
        )
    ),
    query_in_organization=Mock(return_value=None),
    get_organization_by_user_response=Mock(
        return_value=OrganizationResponse(
            id="0123456789ab0123456789ab",
            name="test_org",
            db_connection_id="test_connection_id",
        )
    ),
)
@patch(
    "modules.db_connection.service.DBConnectionService.get_db_connection",
    Mock(return_value=DBConnectionResponse(id="123", alias="test_alias")),
)
class TestQueryAPI(TestCase):
    url = "/query"
    test_header = {"Authorization": "Bearer some-token"}
    test_question = {
        "_id": ObjectId(b"lao-gan-maaa"),
        "question": "test_question",
        "db_connection_id": "0123456789ab0123456789ab",
    }

    test_0 = {
        "_id": ObjectId(b"foo-bar-quux"),
        "question_id": test_question["_id"],
        "response": "test_response",
        "sql_query": "test_query",
        "sql_query_result": {
            "columns": ["test_column"],
            "rows": [{"test_key": "test_value"}],
        },
        "sql_generation_status": "VALID",
        "confidence_score": 0.8,
        "intermediate_steps": ["test_process"],
        "exec_time": 20.0,
        "total_tokens": 100,
        "total_cost": 0.1,
        "error_message": "test_error",
    }

    test_response_0 = {
        "id": str(test_0["_id"]),
        "question_id": str(test_question["_id"]),
        "response": test_0["response"],
        "sql_query": test_0["sql_query"],
        "sql_query_result": test_0["sql_query_result"],
        "sql_generation_status": test_0["sql_generation_status"],
        "confidence_score": test_0["confidence_score"],
        "intermediate_steps": test_0["intermediate_steps"],
        "exec_time": test_0["exec_time"],
        "total_tokens": test_0["total_tokens"],
        "total_cost": test_0["total_cost"],
        "error_message": test_0["error_message"],
    }

    test_ref_1 = {
        "_id": ObjectId(b"doo-ree-miii"),
        "answer_id": test_0["_id"],
        "question_id": test_question["_id"],
        "question_date": "2023-09-15 21:14:29",
        "status": "NOT_VERIFIED",
        "message": None,
        "last_updated": "2023-09-15 21:14:29",
        "updated_by": None,
        "organization_id": ObjectId(b"foo-bar-quux"),
        "display_id": "QR-00000",
        "slack_info": {
            "user_id": "test_user_id",
            "workspace_id": "test_workspace_id",
            "channel_id": "test_channel_id",
            "thread_ts": "test_thread_ts",
            "username": "test_user",
        },
    }

    test_list_response_1 = {
        "id": str(test_ref_1["_id"]),
        "username": "test_user",
        "question": test_question["question"],
        "question_date": test_ref_1["question_date"],
        "response": test_response_0["response"],
        "status": "NOT_VERIFIED",
        "evaluation_score": test_response_0["confidence_score"] * 100.0,
        "display_id": test_ref_1["display_id"],
    }

    test_response_1 = {
        "sql_query": "test_query",
        "sql_query_result": {
            "columns": ["test_column"],
            "rows": [{"test_key": "test_value"}],
        },
        "ai_process": test_response_0["intermediate_steps"],
        "last_updated": test_ref_1["last_updated"],
        "updated_by": None,
        "sql_error_message": "test_error",
        "question_id": str(test_question["_id"]),
        "answer_id": str(test_0["_id"]),
        **test_list_response_1,
    }

    test_slack_response_1 = {
        "id": str(test_ref_1["_id"]),
        "display_id": test_ref_1["display_id"],
        "response": test_response_0["response"],
        "sql_query": test_response_1["sql_query"],
        "exec_time": test_response_0["exec_time"],
        "is_above_confidence_threshold": False,
    }

    test_message_response_1 = {
        "message": "test_response",
    }

    # @patch(
    #     "httpx.AsyncClient.post",
    # @patch(
    #     "modules.organization.service.OrganizationService.get_organization_by_slack_workspace_id",
    #     Mock(
    #     ),
    # @patch(
    # @patch.multiple(
    #     "modules.query.repository.GenerationRepository",
    # def test_answer_question(self):
    #         self.url + "/answer",
    #         },

    # @patch.multiple(
    #     "database.mongo.MongoDB",
    # @patch(
    #     "modules.user.service.UserService.get_user",
    # @patch(
    #     "modules.query.repository.GenerationRepository.get_queries",
    # def test_get_queries(self):

    # @patch.multiple(
    #     "database.mongo.MongoDB",
    # @patch(
    #     "modules.user.service.UserService.get_user",
    # @patch(
    #     "modules.golden_sql.service.GoldenSQLService.get_verified_golden_sql_ref",
    # def test_get_query(self):

    # @patch(
    #     "httpx.AsyncClient.post",
    # @patch.multiple(
    #     "modules.query.repository.GenerationRepository",
    # def test_generate_sql_answer(self):
    #         self.url + "/666f6f2d6261722d71757578/sql-answer",

    # @patch(
    #     "httpx.AsyncClient.patch",
    # @patch.multiple(
    #     "modules.query.repository.GenerationRepository",
    # def test_generate_message(self):
    #         self.url + "/666f6f2d6261722d71757578/message",
