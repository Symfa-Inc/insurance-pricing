<div align="center">

<img src=".assets/logo.png" width="100" alt="Insurance Pricing Logo">

# Insurance Pricing Assistant

Full-stack ML application for estimating annual insurance charges with SHAP-based explainability and LLM-powered interpretation.

**[Live Demo](https://insurance-pricing.symfa.ai/)** · **[GitHub](https://github.com/Symfa-Inc/insurance-pricing)** · **[Confluence](https://symfa.atlassian.net/wiki/spaces/SYMFA/pages/5012094986)**

</div>

## Preview

<div align="center">
<img src=".assets/insurance-pricing.png" width="800" alt="Insurance Pricing Preview">
</div>

## Tech Stack

| Category | Technologies |
|----------|-------------|
| Backend | Python 3.13, FastAPI, Uvicorn |
| Frontend | TypeScript, Next.js, React, Tailwind CSS |
| AI/ML | AutoGluon, SHAP, OpenAI |
| Data | pandas, NumPy, scikit-learn, Pydantic |
| Package Management | uv (backend), pnpm (frontend) |
| Deployment | Docker, GitHub Actions, Google Artifact Registry |

## Getting Started

### Prerequisites

- Python 3.13+ / [uv](https://docs.astral.sh/uv/)
- Node.js 24+ / [pnpm](https://pnpm.io/)

### Installation & Running

```bash
# Backend
cd backend
cp .env.example .env          # Add your OpenAI API key
uv sync
uv run uvicorn insurance_pricing.main:app --reload

# Frontend (in a separate terminal)
cd frontend
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) (frontend) and [http://localhost:8000/docs](http://localhost:8000/docs) (API docs).

## License

[MIT](LICENSE)
