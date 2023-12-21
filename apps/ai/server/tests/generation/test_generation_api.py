from unittest import TestCase

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


class TestGenerationAPI(TestCase):
    test_header = {"Authorization": "Bearer some-token"}

    test_prompt = {}

    test_sql_generation = {}

    test_nl_generation = {}

    test_prompt_response = {}

    test_sql_generation_response = {}

    test_nl_generation_response = {}

    def test_create_prompt(self):
        pass

    def test_create_prompt_sql_generation(self):
        pass

    def test_create_prompt_nl_generation(self):
        pass
