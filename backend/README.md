# Insurance Pricing - Backend

ML service for predicting insurance premiums based on customer input data with explainability (feature importance, SHAP) and executive summary for the user.

## Setup

```bash
# From project root
uv sync --dev
```

## Run

```bash
uv run uvicorn insurance_pricing.main:app --reload
```

## Test

```bash
uv run pytest
```
