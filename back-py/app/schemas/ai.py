from pydantic import BaseModel, Field


class SwitchModelRequest(BaseModel):
    modelId: str = Field(..., min_length=1, description="模型ID")
