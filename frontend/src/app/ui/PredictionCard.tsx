import type { InterpretationPayload, PredictResponse } from "@/app/types/api";
import { InterpretationCard } from "@/app/ui/InterpretationCard";
import { formatCurrencyUSD } from "@/app/ui/StatusSummary";
import { ShapChart } from "@/app/ui/ShapChart";

interface PredictionCardProps {
  result: PredictResponse | null;
  status: "idle" | "pending" | "success" | "error";
  error: string | null;
}

function mergeCaveats(result: PredictResponse): InterpretationPayload | null {
  if (!result.interpretation) {
    return null;
  }

  const mergedCaveats = Array.from(
    new Set([...(result.interpretation.caveats ?? []), ...(result.extrapolation_warnings ?? [])]),
  );

  return {
    ...result.interpretation,
    caveats: mergedCaveats,
  };
}

export function PredictionCard({ result, status, error }: PredictionCardProps) {
  const hasResult = status === "success" && result !== null;
  const interpretationWithCaveats = hasResult ? mergeCaveats(result) : null;
  const extrapolationCaveats = hasResult ? result.extrapolation_warnings ?? [] : [];

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <section>
        {status === "pending" ? (
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
              Estimated annual charges
            </p>
            <h2 className="text-2xl font-semibold text-slate-900">Estimating...</h2>
            <p className="text-sm text-slate-500">Running the model with your submitted inputs.</p>
          </div>
        ) : hasResult ? (
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div className="space-y-3">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                Estimated annual charges
              </p>
              <h2 className="text-2xl font-semibold text-slate-900">Pricing estimate</h2>
              <p className="text-sm text-slate-500">Estimate generated from your submitted profile.</p>
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
        ) : (
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
              Estimated annual charges
            </p>
            <h2 className="text-2xl font-semibold text-slate-900">Estimated annual charges</h2>
            <p className="text-sm text-slate-500">Submit inputs to get an estimate.</p>
          </div>
        )}
      </section>

      {status === "error" && error ? (
        <div className="mt-6 border-t border-slate-100 pt-6">
          <div className="rounded-xl border border-rose-100 bg-rose-50 p-4 text-sm text-rose-700">{error}</div>
        </div>
      ) : null}

      {hasResult ? (
        <div className="mt-6 border-t border-slate-100 pt-6">
          {interpretationWithCaveats ? (
            <InterpretationCard interpretation={interpretationWithCaveats} embedded />
          ) : (
            <section>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Interpretation</p>
              <p className="mt-3 text-sm text-slate-500">Interpretation is not available for this prediction.</p>
              {extrapolationCaveats.length ? (
                <div className="mt-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Caveats</p>
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
      ) : null}

      {hasResult ? (
        <div className="mt-6 border-t border-slate-100 pt-6">
          {result.shap?.contributions?.length ? (
            <ShapChart
              contributions={result.shap.contributions}
              baseValue={result.shap.base_value}
              predictedValue={result.charges}
              embedded
            />
          ) : (
            <section>
              <div className="space-y-2">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Explainability</p>
                <h3 className="text-2xl font-semibold text-slate-900">What influenced the estimate</h3>
              </div>
              <p className="mt-6 text-sm text-slate-500">SHAP contributions are not available for this prediction.</p>
            </section>
          )}
        </div>
      ) : null}

      {hasResult && (result.explainability_error || result.llm_error) ? (
        <div className="mt-6 border-t border-slate-100 pt-6">
          <div className="rounded-xl border border-amber-100 bg-amber-50 p-4 text-sm text-amber-700">
            {result.explainability_error ? `Explainability: ${result.explainability_error}` : null}
            {result.explainability_error && result.llm_error ? " " : null}
            {result.llm_error ? `Interpretation: ${result.llm_error}` : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}
