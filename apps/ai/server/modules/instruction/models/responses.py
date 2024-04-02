from modules.instruction.models.entities import AggrInstruction, Instruction


class InstructionResponse(Instruction):
    metadata: dict | None

    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and dic["metadata"] and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic


class ACInstructionResponse(AggrInstruction):
    pass
