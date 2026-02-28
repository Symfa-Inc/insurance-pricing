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
import { FeaturePanel } from "@/app/ui/FeaturePanel";
import { PageIntro } from "@/app/ui/PageIntro";
import { PredictionCard } from "@/app/ui/PredictionCard";

function toPredictRequest(
  formValues: FeatureFormValues,
  features: readonly FeatureSchema[],
): { payload: PredictRequest | null; error: string | null } {
  const payload: PredictRequest = {
    age: 0,
    sex: "female",
    bmi: 0,
    children: 0,
    smoker: "no",
    region: "northeast",
  };

  for (const feature of features) {
    const rawValue = formValues[feature.id].trim();

    switch (feature.id) {
      case "age": {
        if (rawValue.length === 0) {
          return { payload: null, error: `${feature.label} is required.` };
        }
        const parsed = Number(rawValue);
        if (!Number.isFinite(parsed)) {
          return { payload: null, error: `${feature.label} must be a valid number.` };
        }
        payload.age = parsed;
        break;
      }
      case "bmi": {
        if (rawValue.length === 0) {
          return { payload: null, error: `${feature.label} is required.` };
        }
        const parsed = Number(rawValue);
        if (!Number.isFinite(parsed)) {
          return { payload: null, error: `${feature.label} must be a valid number.` };
        }
        payload.bmi = parsed;
        break;
      }
      case "children": {
        if (rawValue.length === 0) {
          return { payload: null, error: `${feature.label} is required.` };
        }
        const parsed = Number(rawValue);
        if (!Number.isFinite(parsed)) {
          return { payload: null, error: `${feature.label} must be a valid number.` };
        }
        payload.children = parsed;
        break;
      }
      case "sex":
        payload.sex = rawValue as PredictRequest["sex"];
        break;
      case "smoker":
        payload.smoker = rawValue as PredictRequest["smoker"];
        break;
      case "region":
        payload.region = rawValue as PredictRequest["region"];
        break;
      default:
        return { payload: null, error: `Unsupported feature: ${feature.id}` };
    }
  }

  return { payload, error: null };
}

function createInputFingerprint(
  formValues: FeatureFormValues,
  features: readonly FeatureSchema[],
): string {
  const orderedEntries = [...features]
    .map((feature) => feature.id)
    .sort()
    .map((featureId) => [featureId, formValues[featureId]]);

  return JSON.stringify(Object.fromEntries(orderedEntries));
}

export default function Home() {
  const [featureValues, setFeatureValues] = useState<FeatureFormValues>(() =>
    createInitialFeatureValues(FEATURE_SCHEMA),
  );
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [status, setStatus] = useState<"idle" | "pending" | "success" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const [lastSubmittedFingerprint, setLastSubmittedFingerprint] = useState<string | null>(null);
  const currentFingerprint = useMemo(
    () => createInputFingerprint(featureValues, FEATURE_SCHEMA),
    [featureValues],
  );
  const isSubmitting = status === "pending";
  const submitDisabled =
    isSubmitting || (lastSubmittedFingerprint !== null && lastSubmittedFingerprint === currentFingerprint);

  const handleFeatureChange = (id: FeatureSchema["id"], nextValue: string) => {
    setFeatureValues((previous) => ({
      ...previous,
      [id]: nextValue,
    }));
  };

  const handleSubmit = async () => {
    setLastSubmittedFingerprint(currentFingerprint);
    setStatus("pending");
    setError(null);
    setResult(null);
    const { payload, error: validationError } = toPredictRequest(featureValues, FEATURE_SCHEMA);

    if (!payload) {
      setError(validationError ?? "Please review your inputs.");
      setStatus("error");
      return;
    }

    try {
      const data = await predictInsurancePricing(payload);
      setResult(data);
      setStatus("success");
    } catch {
      setError("Unable to estimate charges right now. Please try again.");
      setStatus("error");
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900">
      <main className="mx-auto w-full max-w-5xl px-6 py-10">
        <PageIntro />

        <section className="mt-8 flex flex-col gap-6 md:flex-row md:items-start">
          <div className="w-full md:w-60 md:flex-none">
            <div className="rounded-xl border border-zinc-100 bg-white p-5 shadow-sm">
              <FeaturePanel
                features={FEATURE_SCHEMA}
                values={featureValues}
                onChange={handleFeatureChange}
                onSubmit={handleSubmit}
                isSubmitting={isSubmitting}
                submitDisabled={submitDisabled}
              />
            </div>
          </div>

          <div className="w-full flex-1">
            <PredictionCard result={result} status={status} error={error} />
          </div>
        </section>
      </main>
    </div>
  );
}
