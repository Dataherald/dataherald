import logging
from typing import List

import httpx

from config import DB_ALIAS, DEFAULT_K2_TIMEOUT, K2_CORE_URL
from modules.k2_core.model import DataDefinitionType, SSHSettings

logger = logging.getLogger(__name__)


# use request
class K2Service:
    url = K2_CORE_URL
    timeout = DEFAULT_K2_TIMEOUT
    db_alias = DB_ALIAS

    def answer_question(self, question: str):
        path = "/question"
        data = {"question": question, "db_alias": self.db_alias}

        return self._k2_post_request(path, data)

    def evaluate(self, question: str, golden_sql: str):
        path = "/question/evaluate"
        data = {"question": question, "golden_sql": golden_sql}

        return self._k2_post_request(path, data)

    def connect_database(
        self,
        alias: str,
        use_ssh: bool,
        connection_uri: str | None = None,
        ssh_settings: SSHSettings | None = None,
    ) -> bool:
        path = "/database"
        data = {
            "alias": alias,
            "use_ssh": use_ssh,
            "connection_uri": connection_uri,
            "ssh_settings": ssh_settings,
        }

        return self._k2_post_request(path, data)

    def add_golden_records(self, golden_records: List):
        path = "/golden-record"
        data = {"golden_records": golden_records}

        return self._k2_post_request(path, data)

    def add_data_definition(self, uri: str, type: DataDefinitionType):
        path = "/data-definition"
        data = {"uri": uri, "type": type}

        return self._k2_post_request(path, data)

    def heartbeat(self):
        path = "/heartbeat"
        return self._k2_get_request(path)

    def _k2_post_request(self, path, data):
        with httpx.Client() as client:
            try:
                response = client.post(
                    self.url + path, params=data, timeout=self.timeout
                )
                response.raise_for_status()  # Raise an exception for non-2xx status codes
                return response.json()
            except httpx.HTTPStatusError as e:
                return {
                    "error": f"Request failed with status code: {e.response.status_code}"
                }
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}

    def _k2_get_request(self, path):
        with httpx.Client() as client:
            try:
                response = client.get(self.url + path)
                response.raise_for_status()  # Raise an exception for non-2xx status codes
                return response.json()
            except httpx.HTTPStatusError as e:
                return {
                    "error": f"Request failed with status code: {e.response.status_code}"
                }
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
