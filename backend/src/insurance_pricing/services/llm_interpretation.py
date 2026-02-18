from __future__ import annotations

import json
from typing import Any, Literal

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field

from insurance_pricing.schemas.predict import InterpretationPayload, ShapPayload
from insurance_pricing.settings import Settings


class _LLMTopFeature(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feature: str
    direction: Literal["increases", "decreases", "mixed"]
    strength: Literal["high", "medium", "low"]


class _LLMInterpretationPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    headline: str
    bullets: list[str] = Field(min_length=3, max_length=5)
    caveats: list[str] = Field(min_length=1, max_length=3)
    top_features: list[_LLMTopFeature] = Field(min_length=1, max_length=5)


def _build_interpretation_schema() -> dict[str, Any]:
    schema = _LLMInterpretationPayload.model_json_schema()
    return {
        "name": "prediction_interpretation",
        "strict": True,
        "schema": schema,
    }


INTERPRETATION_SCHEMA = _build_interpretation_schema()


def interpret_shap(
    payload: ShapPayload,
    prediction_charges: float,
    settings: Settings,
) -> InterpretationPayload:
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI not configured")

    client = OpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
    )

    top_three = payload.contributions[:3]
    context_payload = {
        "prediction_charges": prediction_charges,
        "base_value": payload.base_value,
        "top_contributions": [item.model_dump() for item in payload.contributions],
        "context": "This is a local explanation for one prediction.",
    }

    instruction = (
        "You explain one insurance premium prediction. "
        "Focus on the top 3 drivers by absolute SHAP value. "
        "State which features increased or decreased this estimate. "
        "Avoid causal language; use phrases such as 'associated with' or "
        "'contributed to this estimate'. Keep the output concise. "
        "Include caveats that this is a local, model-dependent explanation. "
        f"Top-3 features are: {', '.join(item.feature for item in top_three)}."
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": instruction},
            {
                "role": "user",
                "content": json.dumps(context_payload, separators=(",", ":")),
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": INTERPRETATION_SCHEMA,
        },
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("OpenAI returned an empty interpretation payload")
    structured = json.loads(content)
    llm_payload = _LLMInterpretationPayload.model_validate(structured)
    return InterpretationPayload.model_validate(llm_payload.model_dump())
