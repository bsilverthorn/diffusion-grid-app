import pydantic

from .banana import ModelRunOutputs

class GridPrompt(pydantic.BaseModel):
    text: str
    signature: str

class GridRunStatus(pydantic.BaseModel):
    call_id: str
    message: str

class GridImageInfo(pydantic.BaseModel):
    diffusion: ModelRunOutputs
    signatures: dict[int, str]