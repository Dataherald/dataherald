from modules.golden_sql.models.entities import BaseGoldenSQL


class GoldenSQLRequest(BaseGoldenSQL):
    db_connection_id: str
