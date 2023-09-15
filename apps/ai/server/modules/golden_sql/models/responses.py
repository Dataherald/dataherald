from modules.golden_sql.models.entities import BaseGoldenSQL, GoldenSQLSource


class GoldenSQLResponse(BaseGoldenSQL):
    id: str
    db_connection_id: str | None
    organization_id: str
    display_id: str | None
    verified_query_display_id: str | None
    source: GoldenSQLSource | None
    verified_query_id: str | None
    created_time: str | None
