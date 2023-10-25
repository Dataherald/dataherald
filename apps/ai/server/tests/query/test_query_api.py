from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from app import app
from modules.db_connection.models.responses import DBConnectionResponse
from modules.organization.models.entities import SlackBot, SlackInstallation
from modules.organization.models.responses import OrganizationResponse
from modules.query.models.entities import Query
from modules.user.models.responses import UserResponse

client = TestClient(app)


@patch("utils.auth.VerifyToken.verify", Mock(return_value={"email": ""}))
@patch.multiple(
    "utils.auth.Authorize",
    user=Mock(
        return_value=UserResponse(
            id="123",
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
        "response_id": test_0["_id"],
        "question_id": test_question["_id"],
        "question_date": "2023-09-15 21:14:29",
        "status": "NOT_VERIFIED",
        "custom_response": None,
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

    @patch(
        "httpx.AsyncClient.post",
        AsyncMock(return_value=Response(status_code=201, json=test_response_0)),
    )
    @patch(
        "modules.organization.service.OrganizationService.get_organization_by_slack_workspace_id",
        Mock(
            return_value=OrganizationResponse(
                id="0123456789ab0123456789ab",
                name="test_org",
                db_connection_id="0123456789ab0123456789ab",
                slack_installation=SlackInstallation(bot=SlackBot(token="test_token")),
                confidence_threshold=1.0,
            )
        ),
    )
    @patch(
        "utils.slack.SlackWebClient.get_user_real_name", Mock(return_value="test_user")
    )
    @patch.multiple(
        "modules.query.repository.QueryRepository",
        get_query=Mock(return_value=None),
        get_next_display_id=Mock(return_value="QR-00000"),
        add_query=Mock(return_value=str(test_ref_1["_id"])),
    )
    def test_answer_question(self):
        response = client.post(
            self.url + "/answer",
            headers=self.test_header,
            json={
                "question": "test_question",
                "slack_user_id": "test_user_id",
                "slack_workspace_id": "test_workspace_id",
                "slack_channel_id": "test_channel_id",
                "slack_thread_ts": "test_thread_ts",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == self.test_slack_response_1

    @patch.multiple(
        "database.mongo.MongoDB",
        find=Mock(return_value=[test_0]),
        find_by_object_ids=Mock(return_value=[test_question]),
    )
    @patch(
        "modules.user.service.UserService.get_user",
        Mock(return_value=None),
    )
    @patch(
        "modules.golden_sql.service.GoldenSQLService.get_verified_golden_sql_ref",
        Mock(return_value=None),
    )
    @patch(
        "modules.query.repository.QueryRepository.get_queries",
        Mock(return_value=[Query(**test_ref_1)]),
    )
    def test_get_queries(self):
        response = client.get(self.url + "/list", headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK

    @patch.multiple(
        "database.mongo.MongoDB",
        find_one=Mock(return_value=test_ref_1),
        find_by_object_id=Mock(return_value=test_0),
        find_by_id=Mock(return_value=test_question),
    )
    @patch(
        "modules.user.service.UserService.get_user",
        Mock(return_value=None),
    )
    @patch(
        "modules.golden_sql.service.GoldenSQLService.get_verified_golden_sql_ref",
        Mock(return_value=None),
    )
    def test_get_query(self):
        response = client.get(
            self.url + "/666f6f2d6261722d71757578", headers=self.test_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1

    @patch(
        "modules.organization.service.OrganizationService.get_organization",
        Mock(return_value={"id": "666f6f2d6261722d71757578"}),
    )
    @patch(
        "modules.query.service.QueryService.patch_response",
        AsyncMock(return_value=test_response_1),
    )
    def test_patch_response(self):
        response = client.patch(
            self.url + "/666f6f2d6261722d71757578",
            headers=self.test_header,
            json={"sql_query": "test_query", "query_status": "VERIFIED"},
        )
        assert response.status_code == status.HTTP_200_OK

    @patch(
        "modules.query.service.QueryService.run_response",
        AsyncMock(return_value=test_response_1),
    )
    def test_run_response(self):
        response = client.post(
            self.url + "/666f6f2d6261722d71757578/answer",
            headers=self.test_header,
            json={"sql_query": "test_query"},
        )
        assert response.status_code == status.HTTP_200_OK
