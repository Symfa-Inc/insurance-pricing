"use client";

import { useEffect, useMemo, useState } from "react";

import {
  createInitialFeatureValues,
  FEATURE_SCHEMA,
  type FeatureFormValues,
  type FeatureSchema,
} from "@/app/config/features";
import type { PredictRequest, PredictResponse } from "@/app/types/api";
import { predictInsurancePricing } from "@/app/utils/api";
import { FeaturePanel } from "@/app/ui/FeaturePanel";
import { formatCurrencyUSD } from "@/app/ui/StatusSummary";

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

export default function Home() {
  type LayoutPhase = "center" | "mounting" | "expanded";

  const [formValues, setFormValues] = useState<FeatureFormValues>(() =>
    createInitialFeatureValues(FEATURE_SCHEMA),
  );
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [phase, setPhase] = useState<LayoutPhase>("center");
  const [lastSubmittedPayload, setLastSubmittedPayload] = useState<PredictRequest | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const summaryText = useMemo(
    () => buildPredictionSummary(lastSubmittedPayload, result),
    [lastSubmittedPayload, result],
  );
  const extrapolationCaveats = result?.extrapolation_warnings ?? [];
  const interpretationCaveats = [...(result?.interpretation?.caveats ?? []), ...extrapolationCaveats];

  const handleFeatureChange = (id: FeatureSchema["id"], nextValue: string) => {
    setFormValues((previous) => ({
      ...previous,
      [id]: nextValue,
    }));
  };

  const handleSubmit = async () => {
    setError(null);
    const { payload, error } = toPredictRequest(formValues, FEATURE_SCHEMA);

    if (!payload) {
      setError(error ?? "Please review your inputs.");
      return;
    }

    try {
      setLoading(true);
      const data = await predictInsurancePricing(payload);
      setResult(data);
      setLastSubmittedPayload(payload);
      setPhase("mounting");
      requestAnimationFrame(() => {
        requestAnimationFrame(() => setPhase("expanded"));
      });
    } catch {
      setError("Unable to estimate charges right now. Please try again.");
      setPhase("center");
    } finally {
      setLoading(false);
    }
  };

  const isExpanded = phase !== "center";
  const predictionSectionClass =
    "w-full " +
    (isExpanded
      ? "flex flex-col gap-8 md:flex-row md:items-start"
      : "flex flex-col items-center justify-start");

  return (
    <div
      className="min-h-screen bg-slate-50 text-slate-900"
      style={{
        backgroundImage:
          "radial-gradient(circle at top left, rgba(99,102,241,0.14), transparent 45%), radial-gradient(circle at 30% 20%, rgba(99,102,241,0.12), transparent 40%), radial-gradient(circle at 90% 10%, rgba(148,163,184,0.16), transparent 45%)",
      }}
    >
      <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-10">

        <section className={predictionSectionClass}>
          <div
            className={
              "w-full md:w-72 transform transition-transform duration-500 ease-out " +
              (phase === "center"
                ? "md:translate-x-0"
                : phase === "mounting"
                  ? "md:-translate-x-6"
                  : "md:-translate-x-6")
            }
          >
            <FeaturePanel
              title="Insurance Pricing Inputs"
              features={FEATURE_SCHEMA}
              values={formValues}
              onChange={handleFeatureChange}
              onSubmit={handleSubmit}
              isSubmitting={loading}
              submitDisabled={loading}
              errorMessage={error}
            />
          </div>

          {phase !== "center" && result ? (
            <section
              className={
                "flex-1 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm " +
                "transform transition-all duration-500 ease-out " +
                (phase === "mounting" ? "opacity-0 translate-y-3" : "opacity-100 translate-y-0")
              }
            >
              <section>
                <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                  <div className="space-y-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                      Estimated annual charges
                    </p>
                    <h2 className="text-2xl font-semibold text-slate-900">Pricing estimate</h2>
                    <p className="text-sm text-slate-500">{summaryText}</p>
                    {result.model_version ? (
                      <p className="text-sm text-slate-500">Model version: {result.model_version}</p>
                    ) : null}
                  </div>
                  <div className="rounded-2xl border border-indigo-100 bg-indigo-50 px-6 py-4 text-center">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-400">
                      Estimated Charges
                    </p>
                    <p className="mt-2 text-3xl font-semibold text-indigo-600">
                      {formatCurrencyUSD(result.charges)}
                    </p>
                  </div>
                </div>
              </section>

              <div className="mt-6 border-t border-slate-100 pt-6">
                {result.interpretation ? (
                  <section>
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                      Interpretation
                    </p>
                    <h3 className="mt-3 text-2xl font-semibold text-slate-900">
                      {result.interpretation.headline}
                    </h3>
                    <ul className="mt-4 list-disc space-y-2 pl-5">
                      {result.interpretation.bullets.map((bullet) => (
                        <li key={bullet} className="text-sm text-slate-600">
                          {bullet}
                        </li>
                      ))}
                    </ul>
                    <div className="mt-5">
                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Caveats
                      </p>
                      <ul className="mt-2 list-disc space-y-1 pl-5">
                        {interpretationCaveats.map((caveat) => (
                          <li key={caveat} className="text-xs text-slate-400">
                            {caveat}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </section>
                ) : (
                  <section>
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                      Interpretation
                    </p>
                    <p className="mt-3 text-sm text-slate-500">
                      Interpretation is not available for this prediction.
                    </p>
                    {extrapolationCaveats.length ? (
                      <div className="mt-5">
                        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                          Caveats
                        </p>
                        <ul className="mt-2 list-disc space-y-1 pl-5">
                          {extrapolationCaveats.map((caveat) => (
                            <li key={caveat} className="text-xs text-slate-400">
                              {caveat}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ) : null}
                  </section>
                )}
              </div>

              <div className="mt-6 border-t border-slate-100 pt-6">
                {result.shap?.contributions?.length ? (
                  <section>
                    <div className="space-y-2">
                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Explainability
                      </p>
                      <h3 className="text-2xl font-semibold text-slate-900">What influenced the estimate</h3>
                    </div>
                    <ul className="mt-6 space-y-4">
                      {result.shap.contributions.map((item) => {
                        const maxAbs = Math.max(
                          ...result.shap!.contributions.map((contribution) => contribution.abs_shap_value),
                          1e-9,
                        );
                        const widthPercent = Math.max(4, (item.abs_shap_value / maxAbs) * 100);
                        const isPositive = item.shap_value >= 0;
                        const tone = isPositive
                          ? "bg-gradient-to-r from-indigo-500 to-indigo-300 text-indigo-700"
                          : "bg-gradient-to-r from-rose-500 to-rose-300 text-rose-700";
                        const formattedValue =
                          typeof item.value === "number"
                            ? Number.isInteger(item.value)
                              ? `${item.value}`
                              : item.value.toFixed(2)
                            : item.value;

                        return (
                          <li key={`${item.feature}-${item.value}`} className="space-y-2">
                            <div className="flex items-center justify-between gap-3 text-sm">
                              <span className="font-medium text-slate-700">
                                {item.feature} = {formattedValue}
                              </span>
                              <span className={isPositive ? "text-indigo-600" : "text-rose-600"}>
                                {isPositive ? "+" : "-"}
                                {Math.abs(item.shap_value).toFixed(2)}
                              </span>
                            </div>
                            <div className="h-3 rounded-full bg-slate-100">
                              <div className={`h-3 rounded-full ${tone}`} style={{ width: `${widthPercent}%` }} />
                            </div>
                          </li>
                        );
                      })}
                    </ul>
                  </section>
                ) : (
                  <section>
                    <div className="space-y-2">
                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Explainability
                      </p>
                      <h3 className="text-2xl font-semibold text-slate-900">What influenced the estimate</h3>
                    </div>
                    <p className="mt-6 text-sm text-slate-500">
                      SHAP contributions are not available for this prediction.
                    </p>
                  </section>
                )}
              </div>
              {result.explainability_error || result.llm_error ? (
                <div className="mt-6 border-t border-slate-100 pt-6">
                  <div className="rounded-xl border border-amber-100 bg-amber-50 p-4 text-sm text-amber-700">
                    {result.explainability_error ? `Explainability: ${result.explainability_error}` : null}
                    {result.explainability_error && result.llm_error ? " " : null}
                    {result.llm_error ? `Interpretation: ${result.llm_error}` : null}
                  </div>
                </div>
              ) : null}
            </section>
          ) : null}
        </section>
      </main>
    </div>
  );
}
