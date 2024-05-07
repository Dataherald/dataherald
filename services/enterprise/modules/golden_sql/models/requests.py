from typing import Any

from modules.golden_sql.models.entities import BaseGoldenSQL


class GoldenSQLRequest(BaseGoldenSQL):
    metadata: dict[str, Any] | None = {}
