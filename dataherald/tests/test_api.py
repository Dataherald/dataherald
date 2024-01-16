from fastapi.testclient import TestClient

from dataherald.app import app

client = TestClient(app)

HTTP_200_CODE = 200
HTTP_201_CODE = 201
HTTP_404_CODE = 404


def test_heartbeat():
    response = client.get("/api/v1/heartbeat")
    assert response.status_code == HTTP_200_CODE


def test_scan_all_tables():
    response = client.post(
        "/api/v1/table-descriptions/sync-schemas",
        json={"db_connection_id": "64dfa0e103f5134086f7090c"},
    )
    assert response.status_code == HTTP_201_CODE


def test_scan_one_table():
    try:
        client.post(
            "/api/v1/table-descriptions/sync-schemas",
            json={
                "db_connection_id": "64dfa0e103f5134086f7090c",
                "table_names": ["foo"],
            },
        )
    except ValueError as e:
        assert str(e) == "No table found"
