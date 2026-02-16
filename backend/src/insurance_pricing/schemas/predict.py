from typing import Literal

from pydantic import BaseModel, Field

Sex = Literal["female", "male"]
Smoker = Literal["no", "yes"]
Region = Literal["northeast", "northwest", "southeast", "southwest"]


class PredictRequest(BaseModel):
    age: int = Field(ge=0, le=120)
    sex: Sex
    bmi: float = Field(ge=0.0, le=100.0)
    children: int = Field(ge=0, le=20)
    smoker: Smoker
    region: Region


class PredictResponse(BaseModel):
    charges: float
    model_version: str | None = None
    extrapolation_warnings: list[str] = Field(default_factory=list)
