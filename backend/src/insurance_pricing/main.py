from fastapi import FastAPI

app = FastAPI(
    title="Insurance Pricing",
    description="ML service for predicting insurance premiums based on customer input data with explainability (feature importance, SHAP) and executive summary for the user.",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
