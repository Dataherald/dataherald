from modules.finetuning.models.entities import Finetuning


class FinetuningResponse(Finetuning):
    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic
