from __future__ import annotations

import json
import logging

from openai import OpenAI

from insurance_pricing.config import Settings
from insurance_pricing.schemas import InterpretationPayload, ShapPayload

logger = logging.getLogger(__name__)


def _format_feature_value(value: str | int | float) -> str:
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.1f}"
    return str(value)


def _top_feature_direction(shap_value: float) -> str:
    if shap_value > 0:
        return "increases"
    if shap_value < 0:
        return "decreases"
    return "mixed"


def _top_feature_strength(rank: int) -> str:
    if rank == 0:
        return "high"
    if rank in (1, 2):
        return "medium"
    return "low"


def _clean_bullets(raw_bullets: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for bullet in raw_bullets:
        compact = " ".join(bullet.strip().split())
        if not compact:
            continue
        lowered = compact.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        cleaned.append(compact)
    return cleaned


def _is_low_signal_interpretation(
    interpretation: InterpretationPayload,
    top_features: list[str],
) -> bool:
    if len(interpretation.bullets) < 2:
        return True

    features_lower = [item.lower() for item in top_features]
    bullets_with_feature = 0
    generic_without_features = 0
    generic_tokens = (
        "predicted charge",
        "predicted charges",
        "base value",
        "estimate amount",
    )

    for bullet in interpretation.bullets:
        lowered = bullet.lower()
        has_feature = any(feature in lowered for feature in features_lower)
        if has_feature:
            bullets_with_feature += 1
        elif any(token in lowered for token in generic_tokens):
            generic_without_features += 1

    if bullets_with_feature < 2:
        return True

    return generic_without_features == len(interpretation.bullets)


def generate_fallback_interpretation(
    shap_payload: ShapPayload,
    prediction_charges: float,
) -> InterpretationPayload:
    ranked = sorted(
        shap_payload.contributions,
        key=lambda item: item.abs_shap_value,
        reverse=True,
    )
    top_three = ranked[:3]
    top_features_source = ranked[:5]

    baseline_gap = prediction_charges - shap_payload.base_value
    baseline_relation = "above" if baseline_gap >= 0 else "below"
    driver_names = (
        ", ".join(item.feature for item in top_three[:2]) or "the top features"
    )
    headline = (
        f"Estimate is {baseline_relation} baseline by ${abs(baseline_gap):,.0f}, "
        f"mainly driven by {driver_names}."
    )

    bullets: list[str] = []
    for item in top_three:
        formatted_value = _format_feature_value(item.value)
        delta = f"${abs(item.shap_value):,.0f}"
        if item.shap_value > 0:
            bullets.append(
                f"{item.feature} ({formatted_value}) increased the estimate by about {delta}.",
            )
        elif item.shap_value < 0:
            bullets.append(
                f"{item.feature} ({formatted_value}) decreased the estimate by about {delta}.",
            )
        else:
            bullets.append(
                f"{item.feature} ({formatted_value}) had minimal effect on this estimate.",
            )

    remaining = ranked[3:]
    if remaining:
        remaining_net = sum(item.shap_value for item in remaining)
        direction = "upward" if remaining_net >= 0 else "downward"
        bullets.append(
            f"The remaining features combined for a net {direction} nudge "
            f"of about ${abs(remaining_net):,.0f}.",
        )

    gap_direction = "above" if baseline_gap >= 0 else "below"
    bullets.append(
        f"Overall, this estimate sits ${abs(baseline_gap):,.0f} {gap_direction} "
        f"the baseline average, primarily shaped by {driver_names}.",
    )

    while len(bullets) < 5:
        bullets.append(
            "Smaller remaining features had limited impact compared with the top drivers.",
        )

    return InterpretationPayload.model_validate(
        {
            "headline": headline,
            "bullets": bullets[:5],
            "caveats": [
                "This explanation is for this prediction only.",
                "Contributions reflect model behavior, not causation.",
            ],
            "top_features": [
                {
                    "feature": item.feature,
                    "direction": _top_feature_direction(item.shap_value),
                    "strength": _top_feature_strength(rank),
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

    top_three = sorted(
        payload.contributions,
        key=lambda item: item.abs_shap_value,
        reverse=True,
    )[:3]
    context_payload = json.dumps(
        {
            "prediction_charges": prediction_charges,
            "base_value": payload.base_value,
            "top_contributions": [item.model_dump() for item in payload.contributions],
            "context": "This is a local explanation for one prediction.",
        },
    )

    instruction = (
        "You explain one insurance premium prediction to a non-technical user. "
        "Focus on the top 3 drivers by absolute SHAP value. "
        "Do not use markdown or HTML. "
        "Keep output concise and informative. "
        "Write exactly 1 short headline and 5 bullets. "
        "The first 3 bullets should each cover one top feature: name the feature, "
        "state its value, say whether it pushed the estimate up or down, include "
        "the approximate SHAP magnitude in dollars, and briefly explain WHY this "
        "factor typically affects insurance pricing (e.g., higher health risk, "
        "regional cost differences, actuarial patterns). "
        "The 4th bullet should summarize how the remaining features combined "
        "to nudge the estimate. "
        "The 5th bullet should give a brief overall takeaway comparing the "
        "predicted cost to the baseline average and noting the dominant theme "
        "(e.g., lifestyle-driven, age-driven, region-driven). "
        "Do not repeat prediction_charges or base_value as standalone bullets. "
        "Avoid causal language; describe associations for this one prediction only. "
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

        interpretation = InterpretationPayload.model_validate(parsed)
        interpretation.bullets = _clean_bullets(interpretation.bullets)[:5]

        top_feature_names = [item.feature for item in top_three]
        if _is_low_signal_interpretation(
            interpretation,
            top_features=top_feature_names,
        ):
            llm_error = (
                "LowSignalInterpretation: LLM output was too generic; fallback applied"
            )
            logger.warning("LLM_INTERPRETATION_FAILED: %s", llm_error)
            return fallback, llm_error

        return interpretation, None
    except Exception as exc:  # noqa: BLE001 - /predict must never fail because of LLM
        llm_error = f"{type(exc).__name__}: {exc}"
        logger.warning("LLM_INTERPRETATION_FAILED: %s", llm_error)
        return fallback, llm_error
