from __future__ import annotations

import json
from typing import Literal

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


def _parse_llm_interpretation(
    client: OpenAI,
    *,
    model: str,
    instruction: str,
    context_payload: dict[str, object],
) -> _LLMInterpretationPayload:
    user_payload = json.dumps(context_payload, separators=(",", ":"))

    response = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": user_payload},
        ],
        text_format=_LLMInterpretationPayload,
    )

    if response.status == "incomplete":
        incomplete = response.incomplete_details
        reason = incomplete.reason if incomplete is not None else "unknown"
        raise RuntimeError(f"OpenAI response incomplete: {reason}")

    parsed = response.output_parsed
    if parsed is None:
        if response.refusal:
            raise RuntimeError(f"OpenAI refused interpretation: {response.refusal}")
        raise RuntimeError("OpenAI returned no structured interpretation payload")

    return _LLMInterpretationPayload.model_validate(parsed)


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
        "Do not use any markdown or HTML tags. "
        "Avoid causal language; use phrases such as 'associated with' or "
        "'contributed to this estimate'. Keep the output concise. "
        "Include caveats that this is a local, model-dependent explanation. "
        f"Top-3 features are: {', '.join(item.feature for item in top_three)}."
    )

    llm_payload = _parse_llm_interpretation(
        client,
        model=settings.openai_model,
        instruction=instruction,
        context_payload=context_payload,
    )

    return InterpretationPayload.model_validate(llm_payload.model_dump())
