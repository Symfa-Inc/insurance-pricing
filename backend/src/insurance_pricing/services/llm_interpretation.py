from __future__ import annotations

import json
import logging

from openai import OpenAI

from insurance_pricing.schemas.predict import InterpretationPayload, ShapPayload
from insurance_pricing.settings import Settings

logger = logging.getLogger(__name__)


def generate_fallback_interpretation(
    shap_payload: ShapPayload,
    prediction_charges: float,
) -> InterpretationPayload:
    top_three = shap_payload.contributions[:3]
    top_features_source = shap_payload.contributions[:5]

    bullets = [
        f"Feature {item.feature} contributed {item.shap_value:.2f} to result."
        for item in top_three
    ]

    while len(bullets) < 3:
        bullets.append("Feature baseline contributed 0.00 to result.")

    return InterpretationPayload.model_validate(
        {
            "headline": f"Predicted charge is {prediction_charges:.2f}.",
            "bullets": bullets[:5],
            "caveats": [
                "This explanation is for this prediction only.",
                "Contributions reflect model behavior, not causation.",
            ],
            "top_features": [
                {
                    "feature": item.feature,
                    "direction": (
                        "increases"
                        if item.shap_value > 0
                        else "decreases"
                        if item.shap_value < 0
                        else "mixed"
                    ),
                    "strength": "high"
                    if rank == 0
                    else "medium"
                    if rank in (1, 2)
                    else "low",
                }
                for rank, item in enumerate(top_features_source)
            ],
        },
    )


def interpret_shap(
    payload: ShapPayload,
    prediction_charges: float,
    settings: Settings,
) -> tuple[InterpretationPayload, str | None]:
    fallback = generate_fallback_interpretation(
        shap_payload=payload,
        prediction_charges=prediction_charges,
    )

    if not settings.openai_api_key:
        llm_error = "OPENAI_API_KEY missing"
        logger.warning("LLM_INTERPRETATION_FAILED: %s", llm_error)
        return fallback, llm_error

    client = OpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
    )

    top_three = payload.contributions[:3]
    context_payload = json.dumps(
        {
            "prediction_charges": prediction_charges,
            "base_value": payload.base_value,
            "top_contributions": [item.model_dump() for item in payload.contributions],
            "context": "This is a local explanation for one prediction.",
        },
    )

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

    try:
        response = client.responses.parse(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": context_payload},
            ],
            text_format=InterpretationPayload,
        )

        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError("OpenAI returned no structured interpretation payload")

        return InterpretationPayload.model_validate(parsed), None
    except Exception as exc:  # noqa: BLE001 - /predict must never fail because of LLM
        llm_error = f"{type(exc).__name__}: {exc}"
        logger.warning("LLM_INTERPRETATION_FAILED: %s", llm_error)
        return fallback, llm_error
