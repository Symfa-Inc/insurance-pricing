#!/usr/bin/env python3
"""
End-to-end Exploratory Data Analysis for the US Health Insurance Dataset.
Writes reports/eda_report.md and saves figures to reports/_eda_figures/.
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Callable
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

if __package__ in (None, ""):
    src_dir = Path(__file__).resolve().parents[2]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

from train.settings import get_scripts_settings

matplotlib.use("Agg")

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

SETTINGS = get_scripts_settings()
DATA_PATH = SETTINGS.source_data_path
REPORT_PATH = SETTINGS.eda_report_path
FIGURES_DIR = SETTINGS.eda_figures_dir

FEATURES = ["age", "sex", "bmi", "children", "smoker", "region"]
TARGET = "charges"
NUMERIC_FEATURES = ["age", "bmi", "children", "charges"]
CATEGORICAL_FEATURES = ["sex", "smoker", "region"]


def _df_to_markdown(df: pd.DataFrame, include_index: bool = True) -> str:
    if hasattr(df, "to_markdown") and callable(getattr(df, "to_markdown", None)):
        try:
            return df.to_markdown()
        except Exception:
            pass
    if include_index and df.index is not None and len(df.index) > 0:
        cols = [""] + list(df.columns)
    else:
        cols = list(df.columns)
    headers = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    rows = [headers, sep]
    for idx, r in df.iterrows():
        if include_index and df.index is not None and len(df.index) > 0:
            cells = [str(idx)] + [str(r[c]) for c in df.columns]
        else:
            cells = [str(r[c]) for c in df.columns]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def get_llm_interpretation(
    prompt: str,
    context: str | None = None,
    api_key: str | None = None,
) -> str:
    api_key = api_key or SETTINGS.openai_api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return (
            "[LLM interpretation skipped: OPENAI_API_KEY not set. "
            "Set the environment variable to generate narrative text.]"
        )
    try:
        import httpx
    except ImportError:
        return "[LLM interpretation skipped: httpx not installed.]"

    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-5-nano-2025-08-07",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a data analyst. Write concise, factual interpretations grounded only in the provided data. No speculation.",
                    },
                    {"role": "user", "content": full_prompt},
                ],
                "max_tokens": 500,
                "temperature": 0.3,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001
        return f"[LLM interpretation failed: {exc!s}]"


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    expected = set(FEATURES) | {TARGET}
    if set(df.columns) != expected:
        raise ValueError(f"Expected columns {expected}, got {set(df.columns)}")
    return df


def compute_overview(df: pd.DataFrame) -> dict:
    return {
        "shape": df.shape,
        "dtypes": df.dtypes.to_dict(),
        "missing": df.isna().sum().to_dict(),
        "describe": df.describe(include="all").to_dict(),
    }


def write_overview_section(df: pd.DataFrame, overview: dict, lines: list[str]) -> None:
    lines.append("## Data overview\n")
    lines.append(
        f"- **Shape:** {overview['shape'][0]} rows, {overview['shape'][1]} columns\n",
    )
    lines.append("- **Column types:**\n")
    for col, dtype in overview["dtypes"].items():
        lines.append(f"  - `{col}`: {dtype}\n")
    lines.append("- **Missing values:**\n")
    missing = overview["missing"]
    if sum(missing.values()) == 0:
        lines.append("  - No missing values.\n")
    else:
        for col, count in missing.items():
            if count > 0:
                lines.append(f"  - `{col}`: {count}\n")
    lines.append("\n### Descriptive statistics\n\n")
    lines.append(_df_to_markdown(df.describe(include="all").round(4)))
    lines.append("\n\n")


def plot_numeric_distributions(df: pd.DataFrame, figures_dir: Path) -> list[str]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for col in NUMERIC_FEATURES:
        fig, ax = plt.subplots(figsize=(6, 4))
        df[col].hist(
            bins=min(40, df[col].nunique()),
            ax=ax,
            edgecolor="white",
            alpha=0.8,
        )
        ax.set_title(f"Distribution of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        fpath = figures_dir / f"univariate_{col}.png"
        fig.savefig(fpath, dpi=120, bbox_inches="tight")
        plt.close(fig)
        paths.append(str(fpath))
    return paths


def plot_categorical_counts(df: pd.DataFrame, figures_dir: Path) -> list[str]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for col in CATEGORICAL_FEATURES:
        fig, ax = plt.subplots(figsize=(6, 4))
        counts = df[col].value_counts().sort_index()
        counts.plot(kind="bar", ax=ax, edgecolor="white")
        ax.set_title(f"Counts: {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=0)
        fpath = figures_dir / f"univariate_{col}.png"
        fig.savefig(fpath, dpi=120, bbox_inches="tight")
        plt.close(fig)
        paths.append(str(fpath))
    return paths


def write_univariate_section(
    df: pd.DataFrame,
    numeric_paths: list[str],
    categorical_paths: list[str],
    lines: list[str],
    llm_fn: Callable[[str, str | None], str],
) -> None:
    lines.append("## Univariate analysis\n\n")
    for col, rel_path in zip(NUMERIC_FEATURES, numeric_paths, strict=True):
        lines.append(f"### {col}\n\n")
        lines.append(
            f"![Distribution of {col}]({FIGURES_DIR.name}/{Path(rel_path).name})\n\n",
        )
        context = f"Variable: {col}. Mean={df[col].mean():.2f}, std={df[col].std():.2f}, min={df[col].min()}, max={df[col].max()}."
        prompt = f"Interpret the distribution of '{col}' in one short paragraph."
        lines.append(f"{llm_fn(prompt, context)}\n\n")
    for col, rel_path in zip(CATEGORICAL_FEATURES, categorical_paths, strict=True):
        lines.append(f"### {col}\n\n")
        lines.append(f"![Counts: {col}]({FIGURES_DIR.name}/{Path(rel_path).name})\n\n")
        counts = df[col].value_counts().to_dict()
        context = f"Variable: {col}. Counts: {json.dumps(counts)}."
        prompt = f"Interpret the distribution of '{col}' in one short paragraph."
        lines.append(f"{llm_fn(prompt, context)}\n\n")


def plot_charges_vs_numeric(
    df: pd.DataFrame,
    figures_dir: Path,
) -> list[tuple[str, str]]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    out = []
    for col in ["age", "bmi", "children"]:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(df[col], df[TARGET], alpha=0.4, s=20)
        z = np.polyfit(df[col], df[TARGET], 1)
        p = np.poly1d(z)
        x_line = np.linspace(df[col].min(), df[col].max(), 100)
        ax.plot(x_line, p(x_line), "r-", linewidth=2, label="Trend")
        ax.set_xlabel(col)
        ax.set_ylabel(TARGET)
        ax.set_title(f"{TARGET} vs {col}")
        ax.legend()
        fpath = figures_dir / f"bivariate_charges_vs_{col}.png"
        fig.savefig(fpath, dpi=120, bbox_inches="tight")
        plt.close(fig)
        out.append((col, str(fpath)))
    return out


def plot_charges_vs_categorical(
    df: pd.DataFrame,
    figures_dir: Path,
) -> list[tuple[str, str]]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    out = []
    for col in CATEGORICAL_FEATURES:
        fig, ax = plt.subplots(figsize=(6, 4))
        order = df[col].value_counts().index.tolist()
        sns.boxplot(data=df, x=col, y=TARGET, order=order, ax=ax)
        ax.set_title(f"{TARGET} by {col}")
        ax.tick_params(axis="x", rotation=15)
        fpath = figures_dir / f"bivariate_charges_by_{col}.png"
        fig.savefig(fpath, dpi=120, bbox_inches="tight")
        plt.close(fig)
        out.append((col, str(fpath)))
    return out


def compute_correlations(df: pd.DataFrame) -> pd.DataFrame:
    return df[NUMERIC_FEATURES].corr().round(4)


def test_smoker_effect(df: pd.DataFrame) -> dict:
    grouped = df.groupby("smoker")[TARGET]
    yes_vals = grouped.get_group("yes")
    no_vals = grouped.get_group("no")
    stat, p_value = stats.ttest_ind(yes_vals, no_vals, equal_var=False)
    return {
        "name": "Effect of smoking on charges",
        "H0": "Mean charges are equal for smokers and non-smokers.",
        "H1": "Mean charges differ between smokers and non-smokers.",
        "test": "Welch two-sample t-test",
        "statistic": float(stat),
        "pvalue": float(p_value),
    }


def test_bmi_charges_relationship(df: pd.DataFrame) -> dict:
    stat, p_value = stats.pearsonr(df["bmi"], df[TARGET])
    return {
        "name": "Relationship between BMI and charges",
        "H0": "No linear correlation between BMI and charges (rho = 0).",
        "H1": "There is a linear correlation between BMI and charges (rho != 0).",
        "test": "Pearson correlation test",
        "statistic": float(stat),
        "pvalue": float(p_value),
    }


def test_regional_differences(df: pd.DataFrame) -> dict:
    groups = [
        df.loc[df["region"] == region, TARGET].values
        for region in df["region"].unique()
    ]
    stat, p_value = stats.f_oneway(*groups)
    return {
        "name": "Regional differences in charges",
        "H0": "Mean charges are equal across all regions.",
        "H1": "At least one region has a different mean charge.",
        "test": "One-way ANOVA",
        "statistic": float(stat),
        "pvalue": float(p_value),
    }


def build_report(df: pd.DataFrame, report_path: Path, figures_dir: Path) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)

    def llm(prompt: str, context: str | None = None) -> str:
        return get_llm_interpretation(prompt, context=context)

    lines = [
        "# Exploratory Data Analysis: US Health Insurance Dataset\n\n",
        "## Dataset description\n\n",
        f"Source: `{DATA_PATH.name}`. Features: {', '.join(FEATURES)}. Target: `{TARGET}`.\n\n",
    ]
    overview = compute_overview(df)
    write_overview_section(df, overview, lines)
    numeric_paths = plot_numeric_distributions(df, figures_dir)
    categorical_paths = plot_categorical_counts(df, figures_dir)
    write_univariate_section(df, numeric_paths, categorical_paths, lines, llm)
    for col, fpath in plot_charges_vs_numeric(df, figures_dir):
        lines.append(f"### {TARGET} vs {col}\n\n")
        lines.append(f"![{TARGET} vs {col}]({FIGURES_DIR.name}/{Path(fpath).name})\n\n")
    for col, fpath in plot_charges_vs_categorical(df, figures_dir):
        lines.append(f"### {TARGET} by {col}\n\n")
        lines.append(f"![{TARGET} by {col}]({FIGURES_DIR.name}/{Path(fpath).name})\n\n")
    lines.append("### Correlation matrix\n\n")
    lines.append(_df_to_markdown(compute_correlations(df)))
    lines.append("\n\n")
    for result in [
        test_smoker_effect(df),
        test_bmi_charges_relationship(df),
        test_regional_differences(df),
    ]:
        lines.append(f"### {result['name']}\n\n")
        lines.append(f"- **H0:** {result['H0']}\n")
        lines.append(f"- **H1:** {result['H1']}\n")
        lines.append(f"- **Test:** {result['test']}\n")
        lines.append(f"- **Statistic:** {result['statistic']:.4f}\n")
        lines.append(f"- **p-value:** {result['pvalue']:.4e}\n\n")
    report_path.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_PATH}")
    df = load_data(DATA_PATH)
    build_report(df, REPORT_PATH, FIGURES_DIR)
    print(f"Report written to {REPORT_PATH}")
    print(f"Figures saved to {FIGURES_DIR}")


if __name__ == "__main__":
    main()
