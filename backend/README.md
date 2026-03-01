# 🐍 Insurance Pricing Backend

FastAPI backend for the Insurance Premium Prediction system with ML-powered explainability.

## 📁 Structure

```
backend/
├── src/insurance_pricing/     # Python package (API code)
│   ├── __init__.py            # Package version
│   ├── main.py                # FastAPI app, endpoints, lifespan, CORS
│   ├── config.py              # App settings + path resolution
│   ├── schemas.py             # Pydantic request/response models
│   ├── model.py               # Model/transformer loading + prediction
│   ├── explainability.py      # SHAP computation
│   └── interpretation.py      # OpenAI + fallback interpretation
├── models/                    # Trained ML model artifacts
├── reports/                   # Generated experiment/analysis reports
├── scripts/                   # Training & preprocessing scripts
├── data/                      # Datasets
└── pyproject.toml             # Package dependencies
```

## 🚀 Quick Start

```bash
# From backend/
uv sync
uv run uvicorn insurance_pricing.main:app --reload
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## 📦 Package Management

```bash
# Add a dependency
uv add <package> --package insurance-pricing

# Add a dev dependency
uv add <package> --package insurance-pricing --dev

# Remove a dependency
uv remove <package> --package insurance-pricing
```

## 🧪 Development

```bash
# Run tests
uv run pytest

# Type checking
uv run mypy src/

# Linting & formatting
uv run ruff check src/
uv run ruff format src/
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/predict` | Predict insurance premium |

## ⚙️ Dependency Note (pyproject-compatible)

Ensure these runtime dependencies are available (for `[project.dependencies]`):

```toml
fastapi
uvicorn
pydantic
joblib
numpy
```

## 🧾 Curl Examples

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 41,
    "sex": "female",
    "bmi": 27.3,
    "children": 2,
    "smoker": "no",
    "region": "northwest"
  }'
```

Set a custom artifact path if needed:

```bash
MODEL_PATH=./model.joblib uv run uvicorn insurance_pricing.main:app --reload
```

If the feature transformer is stored in a custom path:

```bash
TRANSFORMER_PATH=./data/feature_transformer.joblib uv run uvicorn insurance_pricing.main:app --reload
```
