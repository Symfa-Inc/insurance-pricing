# 🐍 Insurance Pricing Backend

FastAPI backend for the Insurance Premium Prediction system with ML-powered explainability.

## 📁 Structure

```
backend/
├── src/insurance_pricing/  # Python package (API code)
│   ├── __init__.py
│   └── main.py             # FastAPI application
├── models/                 # Trained ML model artifacts
├── notebooks/              # Jupyter notebooks (EDA, experiments)
├── scripts/                # Training & preprocessing scripts
├── data/                   # Datasets
└── pyproject.toml          # Package dependencies
```

## 🚀 Quick Start

```bash
# From project root
uv sync                     # Install dependencies

# Run the API
uv run uvicorn insurance_pricing.main:app --reload --port 8000
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
| POST | `/explain` | Get SHAP explanations |
