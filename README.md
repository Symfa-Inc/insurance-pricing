<div align="center">

<img src=".assets/logo.png" width="100" alt="Project Logo">

# Insurance Pricing Assistant

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178c6.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![AutoGluon](https://img.shields.io/badge/AutoGluon-Tabular-2C7BE5.svg)](https://auto.gluon.ai/stable/)
[![SHAP](https://img.shields.io/badge/SHAP-Explainability-111111.svg)](https://shap.readthedocs.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-10a37f.svg)](https://platform.openai.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

**A full-stack ML application for estimating annual insurance charges with transparent, human-readable prediction explanations.**

🔗 **Live Demo**: *TODO*

💻 **GitHub**: [https://github.com/Symfa-Inc/insurance-pricing](https://github.com/Symfa-Inc/insurance-pricing)

📘 **Confluence**: [https://symfa.atlassian.net/wiki/x/AQBjLQE](https://symfa.atlassian.net/wiki/x/AQBjLQE)

</div>

## Overview

Insurance Pricing Assistant predicts annual insurance charges from customer profile inputs through a FastAPI backend and a modern Next.js frontend.
Beyond returning a numeric estimate, each prediction includes model transparency signals (SHAP feature contributions) and an LLM-generated interpretation so users can understand the likely drivers behind the result.

The project also includes an evaluation stage that generates Markdown artifacts (`eda_report.md` and `evaluation_report.md`) for reproducible model analysis and communication.

This repository is intended as an ML demonstration system and product prototype, not financial, underwriting, or actuarial advice.

## Key Features

- **Insurance Charges Prediction:** AutoGluon tabular regression for annual charges estimation.
- **SHAP-Based Explainability:** Per-prediction feature contribution outputs.
- **LLM-Powered Interpretation:** Human-readable explanation of model behavior for each prediction.
- **Model Evaluation Reports:** R², MAPE, and SMAPE reporting with business-oriented interpretation.
- **EDA Report Generation:** Exploratory data analysis report generation in Markdown.
- **Modern Interactive UI:** Next.js + React + Tailwind user interface for interactive scoring.
- **API-First Backend:** FastAPI service designed for frontend and programmatic clients.

## Tech Stack

| Category | Technologies |
|---|---|
| Backend | Python 3.13, FastAPI, Pydantic, Uvicorn |
| Frontend | TypeScript, Next.js, React, Tailwind CSS |
| ML | AutoGluon (TabularPredictor), scikit-learn |
| Explainability | SHAP |
| LLM | OpenAI API (structured interpretation generation) |
| Data Processing | pandas, NumPy |
| Package Management | uv (Python), pnpm (Node.js) |
| Deployment | Local runtime, Docker-optional workflows |

## Architecture

```text
+--------------------+
| Frontend (Next.js) |
+---------+----------+
          |
          v
+--------------------+
| FastAPI API Layer  |
+---------+----------+
          |
          v
+-----------------------------+
| Model Artifact (AutoGluon)  |
+---------+-------------------+
          |
          v
+--------------------+
| SHAP Contributions |
+---------+----------+
          |
          v
+------------------------------+
| OpenAI Interpretation Layer  |
+------------------------------+
```

## Evaluation and Reporting

The training/evaluation pipeline includes report generation for both technical and business-facing analysis:

- `ag_metrics.py`-style metric logic is implemented in `backend/src/train/stages/evaluate_model.py`.
- `backend/src/train/stages/evaluate_model.py` computes regression quality metrics.
- Metrics include **R²**, **MAPE**, and **SMAPE**.
- The evaluation stage uses an LLM step to generate plain-language interpretation of metric outcomes.
- `backend/src/train/stages/run_eda.py` produces exploratory data insights.
- Outputs are generated as Markdown files:
  - `backend/reports/eda_report.md`
  - `backend/reports/evaluation_report.md`

## Project Structure

```text
insurance-pricing-assistant/
├── backend/
│   ├── src/insurance_pricing/
│   │   ├── main.py              # FastAPI app, endpoints, lifespan, CORS
│   │   ├── config.py            # App settings + path resolution
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── model.py             # Model/transformer loading + prediction
│   │   ├── explainability.py    # SHAP computation
│   │   └── interpretation.py    # OpenAI + fallback interpretation
│   ├── models/
│   ├── data/
│   ├── reports/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   └── Dockerfile
└── README.md
```

> Note: If Docker is not used in your local setup yet, treat `Dockerfile` as an optional deployment artifact placeholder.

## Getting Started

### Prerequisites

- Python 3.13+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv)
- [pnpm](https://pnpm.io/)
- OpenAI API key

### Installation

```bash
# Clone and enter project root
git clone https://github.com/your-org/insurance-pricing-assistant.git
cd insurance-pricing-assistant

# Install Python dependencies (workspace)
uv sync

# Install frontend dependencies
cd frontend
pnpm install
cd ..
```

### Configuration

Set required environment variables before running:

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

Optional model artifact overrides:

```bash
export MODEL_PATH="backend/models/ag_insurance"
export TRANSFORMER_PATH="backend/models/feature_transformer.joblib"
```

### Running Locally

Backend:

```bash
cd backend
uv run uvicorn insurance_pricing.main:app --reload
```

Frontend:

```bash
cd frontend
pnpm dev
```

Local URLs:

- API docs: http://localhost:8000/docs
- Frontend app: http://localhost:3000

## License

This project is licensed under the Apache License 2.0.
See `LICENSE` for details.
