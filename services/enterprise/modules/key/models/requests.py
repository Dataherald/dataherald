from pydantic import BaseModel


class KeyGenerationRequest(BaseModel):
    name: str
