"use client";

import { useEffect, useMemo, useState } from "react";

import {
  createDefaultInputs,
  FEATURE_DEFINITIONS,
  type FeatureDefinition,
} from "@/app/config/features";
import type { PredictRequest, PredictResponse } from "@/app/types/api";
import { predict } from "@/app/utils/api";
import { FeatureImportance } from "@/app/ui/FeatureImportance";
import { FeaturePanel } from "@/app/ui/FeaturePanel";
import { formatCurrencyUSD, StatusSummary } from "@/app/ui/StatusSummary";

function buildPredictionSummary(inputs: PredictRequest, response: PredictResponse | null): string {
  if (!response) {
    return "Adjust inputs to generate an estimate.";
  }

  const profileDetails = [
    `age ${inputs.age}`,
    `BMI ${inputs.bmi.toFixed(1)}`,
    `${inputs.children} dependents`,
    `smoker ${inputs.smoker}`,
    `${inputs.region} region`,
  ];

  return `Based on the current input profile (${profileDetails.join(", ")}), estimated annual charges are ${formatCurrencyUSD(response.charges)}.`;
}

function groupFeatures(features: readonly FeatureDefinition[]) {
  const sortedFeatures = [...features].sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
  const grouped = new Map<string, FeatureDefinition[]>();

  sortedFeatures.forEach((feature) => {
    const groupName = feature.group ?? "General";
    const current = grouped.get(groupName) ?? [];
    current.push(feature);
    grouped.set(groupName, current);
  });

  return Array.from(grouped.entries()).map(([name, definitions]) => ({
    name,
    definitions,
  }));
}

export default function Home() {
  const [inputs, setInputs] = useState<PredictRequest>(() => createDefaultInputs(FEATURE_DEFINITIONS));
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const groupedFeatures = useMemo(() => groupFeatures(FEATURE_DEFINITIONS), []);

  useEffect(() => {
    const controller = new AbortController();
    const debounceTimer = window.setTimeout(async () => {
      try {
        setIsLoading(true);
        setErrorMessage(null);
        const nextPrediction = await predict(inputs, controller.signal);
        setPrediction(nextPrediction);
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setErrorMessage("Unable to refresh the estimate right now. You can keep adjusting inputs.");
      } finally {
        setIsLoading(false);
      }
    }, 320);

    return () => {
      controller.abort();
      window.clearTimeout(debounceTimer);
    };
  }, [inputs]);

  const summaryText = useMemo(
    () => buildPredictionSummary(inputs, prediction),
    [inputs, prediction],
  );

  const auxFields = useMemo(() => {
    if (!prediction?.model_version) {
      return undefined;
    }

    return [{ label: "Model version", value: prediction.model_version }];
  }, [prediction?.model_version]);

  const handleFeatureChange = (feature: FeatureDefinition, nextValue: string | number) => {
    setInputs((previous) => {
      if (feature.type === "numeric") {
        const parsedValue = Number(nextValue);
        const safeValue = Number.isFinite(parsedValue) ? parsedValue : feature.defaultValue;
        return {
          ...previous,
          [feature.key]: safeValue as PredictRequest[typeof feature.key],
        };
      }

      return {
        ...previous,
        [feature.key]: String(nextValue) as PredictRequest[typeof feature.key],
      };
    });
  };

  return (
    <div className="min-h-screen bg-zinc-50 px-6 py-8 text-zinc-900">
      <main className="mx-auto flex w-full max-w-6xl flex-col gap-6">
        <header>
          <p className="text-sm font-medium uppercase tracking-wide text-zinc-500">
            Insurance Pricing Inputs
          </p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">Inputs</h1>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-zinc-900">Inputs</h2>
            <div className="mt-5 space-y-5">
              {groupedFeatures.map((group) => (
                <div key={group.name}>
                  <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
                    {group.name}
                  </h3>
                  <div className="grid gap-3 md:grid-cols-2">
                    {group.definitions.map((feature) => (
                      <FeaturePanel
                        key={feature.key}
                        feature={feature}
                        value={inputs[feature.key]}
                        onChange={(nextValue) => handleFeatureChange(feature, nextValue)}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>

          <div className="flex flex-col gap-6">
            <StatusSummary
              headline="Estimated annual charges"
              summary={summaryText}
              value={prediction?.charges}
              unit="$"
              auxFields={auxFields}
              isLoading={isLoading}
              errorMessage={errorMessage}
            />
            <FeatureImportance items={prediction?.feature_importance} />
          </div>
        </div>
      </main>
    </div>
  );
}
