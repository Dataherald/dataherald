from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

HTTP_200_CODE = 200


def test_heartbeat():
    response = client.get("/heartbeat")
    assert response.status_code == HTTP_200_CODE
