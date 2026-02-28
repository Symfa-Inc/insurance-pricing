import type { PredictRequest, PredictResponse } from "@/app/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function isPredictResponse(value: unknown): value is PredictResponse {
  if (!value || typeof value !== "object") {
    return false;
  }

  const maybeResponse = value as Partial<PredictResponse>;
  return typeof maybeResponse.charges === "number";
}

export async function predictInsurancePricing(
  payload: PredictRequest,
  signal?: AbortSignal,
): Promise<PredictResponse> {
  const response = await fetch(`${API_BASE_URL}/predict`, {
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
