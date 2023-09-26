from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from app import app
from modules.golden_sql.models.entities import GoldenSQLRef

client = TestClient(app)


@patch("utils.auth.VerifyToken.verify", Mock(return_value={"email": ""}))
@patch.multiple(
    "utils.auth.Authorize",
    user=Mock(
        return_value={
            "id": "123",
            "username": "test_user",
            "organization_id": "0123456789ab0123456789ab",
        }
    ),
    user_and_get_org_id=Mock(return_value="0123456789ab0123456789ab"),
    golden_sql_in_organization=Mock(return_value=None),
)
class TestGoldenSQLAPI(TestCase):
    url = "/golden-sql"
    test_header = {"Authorization": "Bearer some-token"}
    test_1 = {
        "_id": ObjectId(b"foo-bar-quux"),
        "question": "test_question",
        "sql_query": "test_query",
        "db_connection_id": "test_connection_id",
    }

    test_2 = {
        "_id": ObjectId(b"lao-gan-maaa"),
        "question": "test_question",
        "sql_query": "test_query",
        "db_connection_id": "test_connection_id",
    }

    test_ref_1 = {
        "id": None,
        "golden_sql_id": test_1["_id"],
        "organization_id": "test_org_id",
        "source": "VERIFIED_QUERY",
        "query_response_id": ObjectId(b"doo-ree-miii"),
        "created_time": "2023-09-15 21:14:29",
        "display_id": "GS-00001",
    }

    test_ref_2 = {
        "id": None,
        "golden_sql_id": test_2["_id"],
        "organization_id": "test_org_id",
        "source": "VERIFIED_QUERY",
        "query_response_id": ObjectId(b"doo-ree-miii"),
        "created_time": "2023-09-15 21:14:29",
        "display_id": "GS-00002",
    }

    test_response_0 = {
        "id": str(test_1["_id"]),
        "question": "test_question",
        "sql_query": "test_query",
        "db_connection_id": "test_connection_id",
    }

    test_response_1 = {
        "id": str(test_1["_id"]),
        "question": test_1["question"],
        "sql_query": test_1["sql_query"],
        "db_connection_id": test_1["db_connection_id"],
        "organization_id": str(test_ref_1["organization_id"]),
        "verified_query_id": str(test_ref_1["query_response_id"]),
        "display_id": test_ref_1["display_id"],
        "verified_query_display_id": "QR-00001",
        "created_time": test_ref_1["created_time"],
        "source": test_ref_1["source"],
    }

    test_response_2 = {
        "id": str(test_2["_id"]),
        "question": test_2["question"],
        "sql_query": test_2["sql_query"],
        "db_connection_id": test_2["db_connection_id"],
        "organization_id": str(test_ref_2["organization_id"]),
        "verified_query_id": str(test_ref_2["query_response_id"]),
        "display_id": test_ref_2["display_id"],
        "verified_query_display_id": "QR-00002",
        "created_time": test_ref_2["created_time"],
        "source": test_ref_2["source"],
    }

    @patch(
        "database.mongo.MongoDB.find_by_object_ids",
        Mock(return_value=[test_1, test_2]),
    )
    @patch.multiple(
        "modules.golden_sql.repository.GoldenSQLRepository",
        get_golden_sql_refs=Mock(
            return_value=[GoldenSQLRef(**test_ref_1), GoldenSQLRef(**test_ref_2)]
        ),
        get_verified_query_display_id=Mock(side_effect=["QR-00001", "QR-00002"]),
    )
    def test_get_golden_sqls(self):
        response = client.get(self.url + "/list", headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [self.test_response_1, self.test_response_2]

    @patch.multiple(
        "database.mongo.MongoDB",
        find_one=Mock(return_value=test_ref_1),
        find_by_object_id=Mock(return_value=test_1),
    )
    @patch(
        "modules.golden_sql.repository.GoldenSQLRepository.get_verified_query_display_id",
        Mock(return_value="QR-00001"),
    )
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
    @patch.multiple(
        "database.mongo.MongoDB",
        find_one=Mock(return_value=test_ref_1),
        insert_one=Mock(return_value=test_1["_id"]),
    )
    @patch.multiple(
        "modules.golden_sql.service.GoldenSQLService",
        delete_golden_sql=Mock(return_value=None),
    )
    @patch.multiple(
        "modules.golden_sql.repository.GoldenSQLRepository",
        add_golden_sql_ref=Mock(return_value=None),
        get_next_display_id=Mock(return_value="QS-00001"),
        get_verified_query_display_id=Mock(return_value="QR-00001"),
    )
    def test_add_golden_sql(self):
        response = client.post(
            self.url,
            headers=self.test_header,
            json=[
                {
                    "question": "test_question",
                    "sql_query": "test_query",
                    "db_connection_id": "test_connection_id",
                }
            ],
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == self.test_response_1

    @patch(
        "httpx.AsyncClient.delete",
        AsyncMock(return_value=Response(status_code=200, json={"status": True})),
    )
    @patch.multiple(
        "modules.golden_sql.repository.GoldenSQLRepository",
        delete_verified_golden_sql_ref=Mock(return_value=None),
        delete_golden_sql_ref=Mock(return_value=1),
    )
    def test_delete_golden_sql(self):
        response = client.delete(self.url + "/123", headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK
