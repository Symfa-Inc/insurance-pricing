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


class ShapContribution(BaseModel):
    feature: str
    value: str | int | float
    shap_value: float
    abs_shap_value: float


class ShapPayload(BaseModel):
    base_value: float
    contributions: list[ShapContribution]
    top_k: int


class TopFeatureDirection(BaseModel):
    feature: str
    direction: Literal["increases", "decreases", "mixed"]
    strength: Literal["high", "medium", "low"]


class InterpretationPayload(BaseModel):
    headline: str
    bullets: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    top_features: list[TopFeatureDirection] = Field(default_factory=list)


InterpretationSource = Literal["fallback", "OPENAI"]


class PredictResponse(BaseModel):
    charges: float
    model_version: str | None = None
    extrapolation_warnings: list[str] = Field(default_factory=list)
    shap: ShapPayload | None = None
    interpretation: InterpretationPayload | None = None
    interpretation_source: InterpretationSource | None = None
    explainability_error: str | None = None
    llm_error: str | None = None
