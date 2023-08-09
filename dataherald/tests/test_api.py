from fastapi.testclient import TestClient

from dataherald.app import app

client = TestClient(app)

HTTP_200_CODE = 200
HTTP_404_CODE = 404


def test_heartbeat():
    response = client.get("/api/v1/heartbeat")
    assert response.status_code == HTTP_200_CODE


def test_scan_all_tables():
    response = client.post("/api/v1/scanner", json={"db_alias": "foo"})
    assert response.status_code == HTTP_200_CODE


def test_scan_one_table():
    response = client.post(
        "/api/v1/scanner", json={"db_alias": "foo", "table_name": "foo"}
    )
    assert response.status_code == HTTP_404_CODE


def test_answer_question():
    response = client.post(
        "/api/v1/question", json={"question": "Who am I?", "db_alias": "foo"}
    )
    assert response.status_code == HTTP_200_CODE
