from modules.golden_sql.models.entities import GoldenSQL


class GoldenSQLResponse(GoldenSQL):
    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic


class AdminConsoleGoldenSqlResponse(GoldenSQL):
    pass
