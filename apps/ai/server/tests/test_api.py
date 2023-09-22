from unittest import TestCase

from fastapi import status
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


class TestAPI(TestCase):
    def test_heartbeat(self):
        response = client.get("/heartbeat")
        assert response.status_code == status.HTTP_200_OK
