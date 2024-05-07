from fastapi.testclient import TestClient

from dataherald.app import app

client = TestClient(app)

HTTP_200_CODE = 200
HTTP_201_CODE = 201
HTTP_404_CODE = 404


def test_heartbeat():
    response = client.get("/api/v1/heartbeat")
    assert response.status_code == HTTP_200_CODE
