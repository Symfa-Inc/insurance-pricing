#!/usr/bin/env python3
"""
End-to-end Exploratory Data Analysis for the US Health Insurance Dataset.
Writes notebooks/eda_report.md and saves figures to notebooks/_eda_figures/.
"""

from __future__ import annotations

import os
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Headless backend for reproducible runs

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# -----------------------------------------------------------------------------
# Configuration and paths (reproducible, no hard-coded schema beyond given)
# -----------------------------------------------------------------------------

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# Paths: script lives at backend/src/scripts/run_eda.py → backend is parent of src
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_PATH = BACKEND_DIR / "data" / "source.csv"
REPORT_PATH = BACKEND_DIR / "notebooks" / "eda_report.md"
FIGURES_DIR = BACKEND_DIR / "notebooks" / "_eda_figures"

FEATURES = ["age", "sex", "bmi", "children", "smoker", "region"]
TARGET = "charges"
NUMERIC_FEATURES = ["age", "bmi", "children", "charges"]
CATEGORICAL_FEATURES = ["sex", "smoker", "region"]


def _df_to_markdown(df: pd.DataFrame, include_index: bool = True) -> str:
    """Convert DataFrame to Markdown table without requiring tabulate."""
    if hasattr(df, "to_markdown") and callable(getattr(df, "to_markdown", None)):
        try:
            return df.to_markdown()
        except Exception:
            pass
    # Fallback: simple markdown table
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


# -----------------------------------------------------------------------------
# LLM interpretation (narrative only; no computation)
# -----------------------------------------------------------------------------


def get_llm_interpretation(
    prompt: str,
    context: str | None = None,
    api_key: str | None = None,
) -> str:
    """
    Call an LLM to generate narrative interpretation. Used only for text;
    all numbers and decisions come from computed results.
    """
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return (
            "[LLM interpretation skipped: OPENAI_API_KEY not set. "
            "Set the environment variable to generate narrative text.]"
        )

    try:
        import httpx
    except ImportError:
        return "[LLM interpretation skipped: httpx not installed.]"

    full_prompt = prompt
    if context:
        full_prompt = f"{context}\n\n{prompt}"

    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
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
    except Exception as e:
        return f"[LLM interpretation failed: {e!s}]"


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------


def load_data(path: Path) -> pd.DataFrame:
    """Load CSV and validate expected columns."""
    df = pd.read_csv(path)
    expected = set(FEATURES) | {TARGET}
    if set(df.columns) != expected:
        raise ValueError(f"Expected columns {expected}, got {set(df.columns)}")
    return df


# -----------------------------------------------------------------------------
# 1. Data overview
# -----------------------------------------------------------------------------


def compute_overview(df: pd.DataFrame) -> dict:
    """Shape, dtypes, missing counts, and descriptive statistics."""
    overview = {
        "shape": df.shape,
        "dtypes": df.dtypes.to_dict(),
        "missing": df.isna().sum().to_dict(),
        "describe": df.describe(include="all").to_dict(),
    }
    return overview


def write_overview_section(df: pd.DataFrame, overview: dict, lines: list[str]) -> None:
    """Append data overview section to report lines."""
    lines.append("## Data overview\n")
    lines.append(f"- **Shape:** {overview['shape'][0]} rows, {overview['shape'][1]} columns\n")
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
    desc = df.describe(include="all").round(4)
    lines.append(_df_to_markdown(desc))
    lines.append("\n\n")


# -----------------------------------------------------------------------------
# 2. Univariate analysis
# -----------------------------------------------------------------------------


def plot_numeric_distributions(df: pd.DataFrame, figures_dir: Path) -> list[str]:
    """Histograms/KDE for age, bmi, children, charges. Return list of image paths."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, col in enumerate(NUMERIC_FEATURES):
        fig, ax = plt.subplots(figsize=(6, 4))
        df[col].hist(bins=min(40, df[col].nunique()), ax=ax, edgecolor="white", alpha=0.8)
        ax.set_title(f"Distribution of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        fpath = figures_dir / f"univariate_{col}.png"
        fig.savefig(fpath, dpi=120, bbox_inches="tight")
        plt.close(fig)
        paths.append(str(fpath))
    return paths


def plot_categorical_counts(df: pd.DataFrame, figures_dir: Path) -> list[str]:
    """Bar plots for sex, smoker, region. Return list of image paths."""
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
    llm_fn: callable,
) -> None:
    """Append univariate analysis section with plot references and interpretations."""
    lines.append("## Univariate analysis\n\n")
    for col, rel_path in zip(NUMERIC_FEATURES, numeric_paths):
        lines.append(f"### {col}\n\n")
        lines.append(f"![Distribution of {col}]({FIGURES_DIR.name}/{Path(rel_path).name})\n\n")
        context = f"Variable: {col}. Mean={df[col].mean():.2f}, std={df[col].std():.2f}, min={df[col].min()}, max={df[col].max()}."
        interp = llm_fn(f"Interpret the distribution of '{col}' in one short paragraph.", context)
        lines.append(f"{interp}\n\n")
    for col, rel_path in zip(CATEGORICAL_FEATURES, categorical_paths):
        lines.append(f"### {col}\n\n")
        lines.append(f"![Counts: {col}]({FIGURES_DIR.name}/{Path(rel_path).name})\n\n")
        counts = df[col].value_counts().to_dict()
        context = f"Variable: {col}. Counts: {json.dumps(counts)}."
        interp = llm_fn(f"Interpret the distribution of '{col}' in one short paragraph.", context)
        lines.append(f"{interp}\n\n")


# -----------------------------------------------------------------------------
# 3. Bivariate analysis
# -----------------------------------------------------------------------------


def plot_charges_vs_numeric(
    df: pd.DataFrame, figures_dir: Path
) -> list[tuple[str, str]]:
    """Scatter plots of charges vs age, bmi, children with trend lines. Return (col, path)."""
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


def plot_charges_vs_categorical(df: pd.DataFrame, figures_dir: Path) -> list[tuple[str, str]]:
    """Boxplots of charges by sex, smoker, region. Return (col, path)."""
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
    """Pearson correlation matrix for numeric columns."""
    return df[NUMERIC_FEATURES].corr().round(4)


def write_bivariate_section(
    df: pd.DataFrame,
    scatter_paths: list[tuple[str, str]],
    box_paths: list[tuple[str, str]],
    corr: pd.DataFrame,
    lines: list[str],
    llm_fn: callable,
) -> None:
    """Append bivariate section with plots and correlation."""
    lines.append("## Bivariate analysis\n\n")
    lines.append("### Relationship between charges and each feature\n\n")
    for col, fpath in scatter_paths:
        lines.append(f"#### {col}\n\n")
        lines.append(f"![{TARGET} vs {col}]({FIGURES_DIR.name}/{Path(fpath).name})\n\n")
        r, p_val = stats.pearsonr(df[col], df[TARGET])
        context = f"Pearson r({col}, charges) = {r:.4f}, p-value = {p_val:.4e}."
        interp = llm_fn(f"Interpret the relationship between charges and '{col}' in one short paragraph.", context)
        lines.append(f"{interp}\n\n")
    for col, fpath in box_paths:
        lines.append(f"#### {col}\n\n")
        lines.append(f"![{TARGET} by {col}]({FIGURES_DIR.name}/{Path(fpath).name})\n\n")
        means = df.groupby(col)[TARGET].agg(["mean", "count"]).round(2).to_dict()
        context = f"Mean charges by {col}: {json.dumps(means)}."
        interp = llm_fn(f"Interpret how '{col}' relates to charges in one short paragraph.", context)
        lines.append(f"{interp}\n\n")
    lines.append("### Correlation matrix (numeric variables)\n\n")
    lines.append(_df_to_markdown(corr))
    lines.append("\n\n")


# -----------------------------------------------------------------------------
# 4. Hypothesis testing
# -----------------------------------------------------------------------------


def test_smoker_effect(df: pd.DataFrame) -> dict:
    """H0: Mean charges equal for smokers vs non-smokers. H1: Not equal. Welch t-test."""
    g = df.groupby("smoker")[TARGET]
    yes_vals = g.get_group("yes")
    no_vals = g.get_group("no")
    stat, p = stats.ttest_ind(yes_vals, no_vals, equal_var=False)
    return {
        "name": "Effect of smoking on charges",
        "H0": "Mean charges are equal for smokers and non-smokers.",
        "H1": "Mean charges differ between smokers and non-smokers.",
        "test": "Welch two-sample t-test",
        "statistic": float(stat),
        "pvalue": float(p),
        "mean_yes": float(yes_vals.mean()),
        "mean_no": float(no_vals.mean()),
    }


def test_bmi_charges_relationship(df: pd.DataFrame) -> dict:
    """H0: No linear relationship between BMI and charges (rho=0). H1: rho != 0. Pearson."""
    stat, p = stats.pearsonr(df["bmi"], df[TARGET])
    return {
        "name": "Relationship between BMI and charges",
        "H0": "No linear correlation between BMI and charges (rho = 0).",
        "H1": "There is a linear correlation between BMI and charges (rho ≠ 0).",
        "test": "Pearson correlation test",
        "statistic": float(stat),
        "pvalue": float(p),
    }


def test_regional_differences(df: pd.DataFrame) -> dict:
    """H0: Mean charges equal across regions. H1: At least one region differs. One-way ANOVA."""
    groups = [df.loc[df["region"] == r, TARGET].values for r in df["region"].unique()]
    stat, p = stats.f_oneway(*groups)
    return {
        "name": "Regional differences in charges",
        "H0": "Mean charges are equal across all regions.",
        "H1": "At least one region has a different mean charge.",
        "test": "One-way ANOVA",
        "statistic": float(stat),
        "pvalue": float(p),
        "means_by_region": df.groupby("region")[TARGET].mean().round(2).to_dict(),
    }


def write_hypotheses_section(
    results: list[dict], lines: list[str], llm_fn: callable
) -> None:
    """Append hypothesis testing section with interpretations."""
    lines.append("## Hypotheses testing\n\n")
    for r in results:
        lines.append(f"### {r['name']}\n\n")
        lines.append(f"- **Null (H0):** {r['H0']}\n")
        lines.append(f"- **Alternative (H1):** {r['H1']}\n")
        lines.append(f"- **Test:** {r['test']}\n")
        lines.append(f"- **Test statistic:** {r['statistic']:.4f}\n")
        lines.append(f"- **p-value:** {r['pvalue']:.4e}\n\n")
        if "mean_yes" in r:
            context = f"Smoker mean={r['mean_yes']:.2f}, non-smoker mean={r['mean_no']:.2f}, p={r['pvalue']:.4e}."
        elif "means_by_region" in r:
            context = f"Means by region: {r['means_by_region']}. F={r['statistic']:.4f}, p={r['pvalue']:.4e}."
        else:
            context = f"Correlation={r['statistic']:.4f}, p={r['pvalue']:.4e}."
        interp = llm_fn("Interpret this result in plain language (reject or fail to reject H0, and what it means).", context)
        lines.append(f"**Interpretation:** {interp}\n\n")


# -----------------------------------------------------------------------------
# 5. Data preparation insights (five concrete items)
# -----------------------------------------------------------------------------


def write_data_prep_insights(lines: list[str], df: pd.DataFrame) -> None:
    """Append exactly five actionable data preparation insights."""
    lines.append("## Data preparation insights\n\n")
    insights = [
        "**Encoding:** One-hot encode `region` and binary-encode `sex` and `smoker` for linear/tree models; consider target encoding for tree-based models if needed.",
        "**Scaling:** Standardize or min-max scale `age`, `bmi`, and `charges` (target) if using gradient-based or distance-sensitive models.",
        "**Outliers:** Inspect `charges` and `bmi` for extreme values (e.g., IQR rule); consider winsorization or robust scaling for stability.",
        "**Feature interactions:** Add interaction terms such as `smoker * bmi` and `age * bmi` to capture non-additive effects suggested by EDA.",
        "**Target:** Log-transform `charges` if modeling with MSE to reduce right-skew impact and heteroscedasticity.",
    ]
    for i, text in enumerate(insights, 1):
        lines.append(f"{i}. {text}\n\n")


# -----------------------------------------------------------------------------
# 6. Report assembly and main
# -----------------------------------------------------------------------------


def build_report(df: pd.DataFrame, report_path: Path, figures_dir: Path) -> None:
    """Generate full EDA report and save figures."""
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

    scatter_paths = plot_charges_vs_numeric(df, figures_dir)
    box_paths = plot_charges_vs_categorical(df, figures_dir)
    corr = compute_correlations(df)
    write_bivariate_section(df, scatter_paths, box_paths, corr, lines, llm)

    hyp_results = [
        test_smoker_effect(df),
        test_bmi_charges_relationship(df),
        test_regional_differences(df),
    ]
    write_hypotheses_section(hyp_results, lines, llm)

    write_data_prep_insights(lines, df)

    lines.append("## Conclusion\n\n")
    conclusion = llm(
        "Synthesize the main EDA findings for the US Health Insurance dataset in one short paragraph: key drivers of charges, distributional notes, and statistical test outcomes. Be concise and factual.",
        context=f"Hypothesis test summaries: smoking (p={hyp_results[0]['pvalue']:.4e}), BMI correlation (p={hyp_results[1]['pvalue']:.4e}), region ANOVA (p={hyp_results[2]['pvalue']:.4e}).",
    )
    lines.append(f"{conclusion}\n")

    report_path.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    """Load data, run EDA, write report."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_PATH}")
    df = load_data(DATA_PATH)
    build_report(df, REPORT_PATH, FIGURES_DIR)
    print(f"Report written to {REPORT_PATH}")
    print(f"Figures saved to {FIGURES_DIR}")


if __name__ == "__main__":
    main()
