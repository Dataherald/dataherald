from modules.instruction.models.entities import Instruction


class InstructionResponse(Instruction):
    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic
