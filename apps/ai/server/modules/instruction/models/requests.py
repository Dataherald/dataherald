from typing import Any

from modules.instruction.models.entities import BaseInstruction


class InstructionRequest(BaseInstruction):
    metadata: dict[str, Any] | None = {}
