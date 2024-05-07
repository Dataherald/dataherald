from modules.golden_sql.models.entities import AggrGoldenSQL, GoldenSQL


class GoldenSQLResponse(GoldenSQL):
    metadata: dict | None

    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and dic["metadata"] and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic


class ACGoldenSQLResponse(AggrGoldenSQL):
    pass
