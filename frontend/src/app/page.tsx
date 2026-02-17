"use client";

import { useMemo, useState } from "react";

import {
  createInitialFeatureValues,
  FEATURE_SCHEMA,
  type FeatureFormValues,
  type FeatureSchema,
} from "@/app/config/features";
import type { PredictRequest, PredictResponse } from "@/app/types/api";
import { predictInsurancePricing } from "@/app/utils/api";
import { FeatureImportance } from "@/app/ui/FeatureImportance";
import { FeaturePanel } from "@/app/ui/FeaturePanel";
import { StatusSummary, formatCurrencyUSD } from "@/app/ui/StatusSummary";

function buildPredictionSummary(payload: PredictRequest | null, response: PredictResponse | null): string {
  if (!payload || !response) {
    return "Adjust inputs to generate an estimate.";
  }

  const details = [
    `age ${payload.age}`,
    `BMI ${payload.bmi}`,
    `${payload.children} dependents`,
    `smoker ${payload.smoker}`,
    `${payload.region} region`,
  ];

  return `Estimate generated from the submitted profile (${details.join(", ")}): ${formatCurrencyUSD(response.charges)} per year.`;
}

function toPredictRequest(
  formValues: FeatureFormValues,
  features: readonly FeatureSchema[],
): { payload: PredictRequest | null; error: string | null } {
  const payload: Partial<PredictRequest> = {};

  for (const feature of features) {
    const rawValue = formValues[feature.id].trim();

    if (feature.type === "number") {
      if (rawValue.length === 0) {
        return { payload: null, error: `${feature.label} is required.` };
      }

      const parsed = Number(rawValue);
      if (!Number.isFinite(parsed)) {
        return { payload: null, error: `${feature.label} must be a valid number.` };
      }

      payload[feature.id] = parsed as PredictRequest[typeof feature.id];
      continue;
    }

    payload[feature.id] = rawValue as PredictRequest[typeof feature.id];
  }

  return { payload: payload as PredictRequest, error: null };
}

export default function Home() {
  const [formValues, setFormValues] = useState<FeatureFormValues>(() =>
    createInitialFeatureValues(FEATURE_SCHEMA),
  );
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [lastSubmittedPayload, setLastSubmittedPayload] = useState<PredictRequest | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const summaryText = useMemo(
    () => buildPredictionSummary(lastSubmittedPayload, prediction),
    [lastSubmittedPayload, prediction],
  );

  const handleFeatureChange = (id: FeatureSchema["id"], nextValue: string) => {
    setFormValues((previous) => ({
      ...previous,
      [id]: nextValue,
    }));
  };

  const handleSubmit = async () => {
    setSubmitError(null);
    const { payload, error } = toPredictRequest(formValues, FEATURE_SCHEMA);

    if (!payload) {
      setSubmitError(error ?? "Please review your inputs.");
      return;
    }

    try {
      setIsSubmitting(true);
      const response = await predictInsurancePricing(payload);
      setPrediction(response);
      setLastSubmittedPayload(payload);
    } catch {
      setSubmitError("Unable to estimate charges right now. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="min-h-screen bg-slate-50 text-slate-900"
      style={{
        backgroundImage:
          "radial-gradient(circle at top left, rgba(99,102,241,0.14), transparent 45%), radial-gradient(circle at 30% 20%, rgba(99,102,241,0.12), transparent 40%), radial-gradient(circle at 90% 10%, rgba(148,163,184,0.16), transparent 45%)",
      }}
    >
      <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-10 md:flex-row">
        <FeaturePanel
          title="Insurance Pricing Inputs"
          features={FEATURE_SCHEMA}
          values={formValues}
          onChange={handleFeatureChange}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
        />

        <section className="flex-1">
          <div className="space-y-8 md:sticky md:top-8 md:self-start">
            <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Inputs</p>
              <h1 className="mt-3 text-3xl font-semibold text-slate-900">Estimated annual charges</h1>
              <p className="mt-3 text-sm text-slate-500">
                Submit inputs from the sidebar to generate a pricing estimate.
              </p>
            </div>

            <StatusSummary
              headline="Estimated annual charges"
              summary={summaryText}
              value={prediction?.charges ?? null}
              modelVersion={prediction?.model_version}
            />

            {submitError ? (
              <div className="rounded-2xl border border-rose-100 bg-rose-50 p-6 text-sm text-rose-700 shadow-sm">
                {submitError}
              </div>
            ) : null}

            {prediction?.feature_importance ? (
              <FeatureImportance items={prediction.feature_importance} />
            ) : (
              <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
                <div className="space-y-2">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                    Explainability
                  </p>
                  <h3 className="text-2xl font-semibold text-slate-900">What influenced the estimate</h3>
                </div>
                <p className="mt-6 text-sm text-slate-500">
                  Feature importance not available for this model yet.
                </p>
              </section>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
