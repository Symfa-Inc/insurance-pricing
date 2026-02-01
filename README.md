<div align="center">

<img src="https://via.placeholder.com/150?text=Logo" width="100" alt="Insurance Pricing Logo">

# 💰 Insurance Premium Pricing

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178c6.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![SHAP](https://img.shields.io/badge/SHAP-0.44-000000.svg)](https://shap.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

**ML service for predicting insurance premiums based on customer input data with explainability (feature importance, SHAP) and executive summary for the user.**

🔗 **Live Demo**: [insurance-pricing-demo.symfa.com](https://insurance-pricing-demo-placeholder.vercel.app/)

</div>


## 📋 Overview

This project demonstrates a transparent approach to insurance pricing using machine learning. Based on the [US Health Insurance Dataset](https://www.kaggle.com/datasets/teertha/ushealthinsurancedataset) from Kaggle, the system predicts premiums while prioritizing explainability. Instead of a black-box output, it provides a detailed breakdown of how individual customer factors—such as age, BMI, and region—drive the calculated cost, helping business users understand the "why" behind every price.

## 🎯 Problem Statement

The goal is to build a predictive model that estimates insurance premiums based on customer characteristics, providing:

- Accurate premium predictions based on customer attributes
- Explainability via feature importance and SHAP values
- Executive summary generation in human-readable language
- Interactive parameter adjustment with real-time updates

## 📁 Project Structure

```
insurance-pricing/
├── backend/                        # 🐍 Python Backend (UV workspace member)
│   ├── src/insurance_pricing/      # FastAPI application
│   │   ├── __init__.py
│   │   └── main.py                 # API endpoints
│   ├── models/                     # Trained ML model artifacts
│   ├── notebooks/                  # Jupyter notebooks (EDA, experiments)
│   ├── scripts/                    # Training & preprocessing scripts
│   ├── data/                       # Datasets
│   │   └── source.csv
│   └── pyproject.toml              # Backend dependencies
│
├── frontend/                       # ⚛️ Next.js Frontend
│   ├── src/app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   └── package.json
│
├── pyproject.toml                  # UV workspace definition
├── uv.lock                         # Lockfile
├── .pre-commit-config.yaml         # Code quality hooks
└── README.md
```

## 📊 Dataset

The dataset contains health insurance records with the following features:

### Customer Demographics
| Feature | Description |
|---------|-------------|
| `age` | Age of the primary beneficiary |
| `sex` | Gender (male/female) |
| `bmi` | Body mass index |
| `children` | Number of dependents covered |
| `smoker` | Smoking status (yes/no) |
| `region` | Residential area in the US |

### Target Variable
| Feature | Description |
|---------|-------------|
| `charges` | **Target** - Individual medical costs billed by insurance |

## 🛠️ Tech Stack

### Backend
- **Python 3.13+**
- **FastAPI** - Modern, high-performance web framework
- **Pydantic** - Data validation
- **uvicorn** - ASGI server

### Frontend
- **Next.js 16** - React framework with SSR
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS 4** - Utility-first CSS framework
- **React 19**

### ML & Data Science
- **pandas** - Data manipulation
- **scikit-learn** - Machine learning
- **SHAP** - Model explainability

### Development
- **uv** - Fast Python package manager
- **pnpm** - Fast Node.js package manager
- **pre-commit** - Git hooks for code quality
- **ruff** - Linter and formatter
- **mypy** - Static type checker

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Node.js 20+
- [pnpm](https://pnpm.io/) (fast and efficient Node.js package manager)
- [uv](https://github.com/astral-sh/uv) (recommended for Python)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Symfa-Inc/insurance-pricing.git
   cd insurance-pricing
   ```

2. **Install Python dependencies:**
   ```bash
   uv sync
   ```

3. **Install frontend dependencies:**
   ```bash
   cd frontend
   pnpm install
   ```

### Running the Application

**Backend (FastAPI):**
```bash
uv run uvicorn insurance_pricing.main:app --reload
```
API will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

**Frontend (Next.js):**
```bash
cd frontend
pnpm dev
```
Frontend will be available at: http://localhost:3000

## 🔗 References

- [US Health Insurance Dataset on Kaggle](https://www.kaggle.com/datasets/teertha/ushealthinsurancedataset)
- [SHAP Documentation](https://shap.readthedocs.io/)
