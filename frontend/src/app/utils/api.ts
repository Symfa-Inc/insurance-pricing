import type { PredictRequest, PredictResponse } from "@/app/types/api";
import type { EdaReportResponse, EvaluationReportResponse } from "@/app/types/reports";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function isPredictResponse(value: unknown): value is PredictResponse {
  if (!value || typeof value !== "object") {
    return false;
  }

  const maybeResponse = value as Partial<PredictResponse>;
  return typeof maybeResponse.charges === "number";
}

function isEdaReportResponse(value: unknown): value is EdaReportResponse {
  if (!value || typeof value !== "object") {
    return false;
  }

  const maybeResponse = value as Partial<EdaReportResponse>;
  return (
    typeof maybeResponse.title === "string" &&
    typeof maybeResponse.markdown === "string" &&
    typeof maybeResponse.assets_base_url === "string"
  );
}

function isEvaluationReportResponse(value: unknown): value is EvaluationReportResponse {
  if (!value || typeof value !== "object") {
    return false;
  }

  const maybeResponse = value as Partial<EvaluationReportResponse>;
  return typeof maybeResponse.title === "string" && typeof maybeResponse.markdown === "string";
}

export async function predictInsurancePricing(
  payload: PredictRequest,
  signal?: AbortSignal,
): Promise<PredictResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    signal,
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Prediction request failed with status ${response.status}`);
  }

  const data: unknown = await response.json();

  if (!isPredictResponse(data)) {
    throw new Error("Prediction response has an unexpected shape");
  }

  return data;
}

export async function getEdaReport(signal?: AbortSignal): Promise<EdaReportResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/reports/eda`, {
    method: "GET",
    signal,
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`EDA report request failed with status ${response.status}`);
  }

  const data: unknown = await response.json();
  if (!isEdaReportResponse(data)) {
    throw new Error("EDA report response has an unexpected shape");
  }

  return data;
}

export async function getEvaluationReport(signal?: AbortSignal): Promise<EvaluationReportResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/reports/evaluation`, {
    method: "GET",
    signal,
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Evaluation report request failed with status ${response.status}`);
  }

  const data: unknown = await response.json();
  if (!isEvaluationReportResponse(data)) {
    throw new Error("Evaluation report response has an unexpected shape");
  }

  return data;
}
