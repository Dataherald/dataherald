from modules.golden_sql.models.entities import GoldenSQL, GoldenSQLSource


class GoldenSQLResponse(GoldenSQL):
    id: str
    question: str
    sql_query: str
    db_alias: str
    organization_id: str
    source: GoldenSQLSource | None
    verified_query_id: str | None
    created_time: str | None
