import type { PredictResponse } from "@/app/types/api";
import { InterpretationCard } from "@/app/ui/InterpretationCard";
import { ShapChart } from "@/app/ui/ShapChart";
import { StatusSummary } from "@/app/ui/StatusSummary";

interface ResultsBubbleProps {
  result: PredictResponse;
  summary: string;
  className?: string;
}

export function ResultsBubble({ result, summary, className = "" }: ResultsBubbleProps) {
  return (
    <section
      className={`rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition-all duration-500 ease-out ${className}`}
    >
      <StatusSummary
        headline="Estimated annual charges"
        summary={summary}
        value={result.charges}
        modelVersion={result.model_version}
        embedded
      />

      <div className="mt-6 border-t border-slate-100 pt-6">
        {result.interpretation ? (
          <InterpretationCard interpretation={result.interpretation} embedded />
        ) : (
          <section>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Interpretation</p>
            <p className="mt-3 text-sm text-slate-500">Interpretation is not available for this prediction.</p>
          </section>
        )}
      </div>

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

      {result.explainability_error || result.llm_error || result.extrapolation_warnings?.length ? (
        <div className="mt-6 border-t border-slate-100 pt-6">
          <div className="rounded-xl border border-amber-100 bg-amber-50 p-4 text-sm text-amber-700">
            {result.explainability_error ? `Explainability: ${result.explainability_error}` : null}
            {result.explainability_error && result.llm_error ? " " : null}
            {result.llm_error ? `Interpretation: ${result.llm_error}` : null}
            {(result.explainability_error || result.llm_error) && result.extrapolation_warnings?.length
              ? " "
              : null}
            {result.extrapolation_warnings?.length ? result.extrapolation_warnings.join(" ") : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}
