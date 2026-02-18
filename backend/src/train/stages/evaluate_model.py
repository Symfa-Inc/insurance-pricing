"""
Shared metrics for AutoGluon training and loading.

Custom metrics must live in an importable module so the saved predictor
can be unpickled when loaded from other scripts (e.g. evaluate_model).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
from autogluon.tabular import TabularPredictor
from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field
from sklearn.metrics import r2_score

if __package__ in (None, ""):
    src_dir = Path(__file__).resolve().parents[2]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

from train.stages.prepare_data import TARGET_COLUMN, InsuranceDataTransformer


def _mape_score(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-8) -> float:
    """Mean absolute percentage error (fraction). Denominator clamped to avoid div by zero."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.maximum(np.abs(y_true), epsilon)
    return float(np.mean(np.abs(y_true - y_pred) / denom))


def _smape_score(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    epsilon: float = 1e-8,
) -> float:
    """Symmetric mean absolute percentage error (fraction)."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    numerator = np.abs(y_true - y_pred)
    denominator = np.abs(y_true) + np.abs(y_pred) + epsilon
    return float(np.mean(numerator / denominator))


class _InterpretationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bullets: list[str] = Field(min_length=3, max_length=6)


def _build_interpretation_schema() -> dict[str, Any]:
    return {
        "name": "evaluation_interpretation",
        "strict": True,
        "schema": _InterpretationResponse.model_json_schema(),
    }


INTERPRETATION_SCHEMA = _build_interpretation_schema()


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return {
        "R²": float(r2_score(y_true, y_pred)),
        "MAPE": float(_mape_score(y_true, y_pred) * 100.0),
        "SMAPE": float(_smape_score(y_true, y_pred) * 100.0),
    }


def render_markdown(
    metrics: dict[str, float],
    interpretation_text: str,
    n_test: int | None = None,
    model_dir_name: str = "ag_insurance",
) -> str:
    safe_interpretation = interpretation_text.strip().replace("$", r"\$")
    test_line = (
        f"- **Test set:** {n_test} rows (holdout from prepared data)\n"
        if n_test is not None
        else "- **Test set:** holdout from prepared data\n"
    )
    lines = [
        "# Model evaluation report\n\n",
        "## Setup\n\n",
        f"- **Model:** AutoGluon predictor loaded from `{model_dir_name}/`\n",
        test_line,
        "- **Target:** charges (in original dollars; predictions inverse-transformed from log-scale)\n\n",
        "## Metrics\n\n",
        "| Metric | Value |\n",
        "|--------|--------|\n",
        f"| R² | {metrics['R²']:.4f} |\n",
        f"| MAPE | {metrics['MAPE']:.2f} % |\n",
        f"| SMAPE | {metrics['SMAPE']:.2f} % |\n\n",
        "## Interpretation\n\n",
        safe_interpretation,
        "\n",
    ]
    return "".join(lines)


def _llm_interpretation(metrics: dict[str, float]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is required for interpretation generation.",
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    timeout_seconds = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "15"))
    client = OpenAI(api_key=api_key, timeout=timeout_seconds)

    prompt_payload = {
        "task": "Translate these exact regression results into plain-language business interpretation.",
        "audience": "non-technical stakeholder unfamiliar with statistical metrics",
        "metrics": {
            "r2": float(metrics["R²"]),
            "mape_percent": float(metrics["MAPE"]),
            "smape_percent": float(metrics["SMAPE"]),
        },
        "target_context": {
            "target_name": "annual insurance charges (USD)",
            "distribution_note": "charges are positive and right-skewed",
            "evaluation_type": "out-of-sample test data",
        },
        "instructions": [
            "Each bullet MUST explicitly restate the numeric value.",
            "Convert R² into percentage of variance explained and interpret whether that is strong, moderate, or weak.",
            "Convert MAPE into a dollar example using a $10,000 charge.",
            "Explain SMAPE in practical terms without defining the formula.",
            "Avoid generic metric definitions.",
            "Avoid abstract phrases like 'summarizes goodness of fit'.",
            "Speak as if explaining to an executive.",
            "Use concrete language like 'this means', 'in practice', 'for example'.",
            "Provide 3–5 concise bullets.",
        ],
    }

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You explain regression evaluation results to a non-technical business stakeholder. "
                    "Do NOT define metrics abstractly. "
                    "Do NOT describe what R², MAPE, or SMAPE mean in general terms. "
                    "Instead, interpret the PROVIDED NUMERIC VALUES and translate them into plain language. "
                    "Each explanation must restate the number and explain what that number implies "
                    "about this specific model’s performance in practical terms. "
                    "Assume the reader has never heard of these metrics."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(prompt_payload, separators=(",", ":")),
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": INTERPRETATION_SCHEMA,
        },
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("OpenAI returned an empty interpretation response.")
    parsed = _InterpretationResponse.model_validate(json.loads(content))
    return "\n".join(f"- {line}" for line in parsed.bullets)


def _load_predictor_and_transformer(
    model_dir: Path,
    transformer_path: Path,
) -> tuple[TabularPredictor, InsuranceDataTransformer]:
    if not model_dir.exists():
        raise FileNotFoundError(
            f"Model not found: {model_dir}. Run train_model.py first.",
        )
    if not transformer_path.exists():
        raise FileNotFoundError(
            f"Transformer artifact not found: {transformer_path}. Run prepare_data.py first.",
        )
    predictor = TabularPredictor.load(str(model_dir))
    transformer = InsuranceDataTransformer.load(transformer_path)
    return predictor, transformer


def evaluate(
    test_path: Path,
    model_dir: Path,
    transformer_path: Path,
    report_path: Path,
) -> dict[str, float]:
    import pandas as pd

    if not test_path.exists():
        raise FileNotFoundError(
            f"Test data not found: {test_path}. Run prepare_data.py first.",
        )

    predictor, transformer = _load_predictor_and_transformer(
        model_dir=model_dir,
        transformer_path=transformer_path,
    )
    test_df = pd.read_csv(test_path)
    if TARGET_COLUMN not in test_df.columns:
        raise ValueError(f"Test data must contain target column '{TARGET_COLUMN}'.")

    x_test = test_df.drop(columns=[TARGET_COLUMN])
    y_test_transformed = test_df[TARGET_COLUMN].values
    pred_transformed = predictor.predict(x_test).values

    y_true = transformer.inverse_transform_target(y_test_transformed)
    y_pred = transformer.inverse_transform_target(pred_transformed)

    metrics = compute_metrics(y_true=y_true, y_pred=y_pred)
    interpretation_text = _llm_interpretation(metrics)
    report = render_markdown(
        metrics=metrics,
        interpretation_text=interpretation_text,
        n_test=len(y_true),
        model_dir_name=model_dir.name,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return metrics


def main() -> None:
    """
    Run evaluation from CLI and write Markdown report.

    This keeps metrics definitions importable for AutoGluon unpickling while
    also allowing this file to be executed as a standalone script.
    """
    from train.settings import get_scripts_settings

    settings = get_scripts_settings()
    parser = argparse.ArgumentParser(
        description="Evaluate model on test CSV and write evaluation report.",
    )
    parser.add_argument(
        "--test-path",
        type=Path,
        default=settings.test_data_path,
        help="Path to prepared test.csv.",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=settings.predictor_dir,
        help="Path to trained predictor directory.",
    )
    parser.add_argument(
        "--transformer-path",
        type=Path,
        default=settings.transformer_path,
        help="Path to feature_transformer.joblib.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=settings.evaluation_report_path,
        help="Output path for evaluation_report.md.",
    )
    args = parser.parse_args()

    metrics = evaluate(
        test_path=args.test_path,
        model_dir=args.model_dir,
        transformer_path=args.transformer_path,
        report_path=args.report_path,
    )
    print(f"Evaluation report saved to {args.report_path}")
    for name, value in metrics.items():
        unit = " %" if name in {"MAPE", "SMAPE"} else ""
        print(f"  {name}: {value:.4f}{unit}")


if __name__ == "__main__":
    main()
