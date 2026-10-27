import pytest
from fastapi.testclient import TestClient

from insurance_pricing.main import app, settings


def test_predict_with_bundled_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "openai_api_key", None)

    with TestClient(app) as client:
        response = client.post(
            "/predict",
            json={
                "age": 35,
                "sex": "female",
                "bmi": 27.5,
                "children": 1,
                "smoker": "yes",
                "region": "northeast",
            },
        )

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["charges"] == pytest.approx(20291.66, abs=0.01)
    assert result["explainability_error"] is None
    assert {item["feature"] for item in result["shap"]["contributions"]} == {
        "age",
        "sex",
        "bmi",
        "children",
        "smoker",
        "region",
    }
    assert result["interpretation"]["headline"]
    assert len(result["interpretation"]["bullets"]) == 5
    assert result["interpretation_source"] == "fallback"
