import type { PredictResponse } from "@/app/types/api";
import { InterpretationCard } from "@/app/ui/InterpretationCard";
import { ShapChart } from "@/app/ui/ShapChart";
import { Tooltip } from "@/app/ui/Tooltip";

interface PredictionCardProps {
  result: PredictResponse | null;
  status: "idle" | "pending" | "success" | "error";
  error: string | null;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(value);
}

export function PredictionCard({ result, status, error }: PredictionCardProps) {
  const hasResult = status === "success" && result !== null;

  if (status === "idle") {
    return (
      <div className="flex h-full min-h-48 items-center justify-center rounded-xl border border-dashed border-zinc-200 p-12">
        <p className="text-sm text-zinc-400">
          Enter your details and click Estimate
        </p>
      </div>
    );
  }

  if (status === "pending") {
    return (
      <div className="flex h-full min-h-48 items-center justify-center rounded-xl border border-zinc-100 bg-white p-12 shadow-sm">
        <div className="flex flex-col items-center gap-3">
          <svg
            className="h-5 w-5 animate-spin text-zinc-400"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="2"
              className="opacity-20"
            />
            <path
              d="M12 2a10 10 0 0 1 10 10"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
          <p className="text-sm text-zinc-400">Running estimate...</p>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="rounded-xl border border-red-100 bg-red-50 px-5 py-4">
        <p className="text-sm text-red-600">{error}</p>
      </div>
    );
  }

  if (!hasResult) return null;

  return (
    <div className="space-y-4">
      {/* Price */}
      <div className="animate-fade-in-up relative rounded-xl border border-zinc-100 bg-white p-6 shadow-sm">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-400 to-transparent" />
        <div className="flex items-center gap-1.5">
          <p className="text-xs font-medium uppercase tracking-wider text-zinc-400">
            Estimated Annual Charges
          </p>
          <Tooltip text="Predicted annual insurance cost based on the inputs you provided." />
        </div>
        <p className="mt-3 font-mono text-4xl font-semibold tracking-tight text-zinc-900">
          {formatCurrency(result.charges)}
        </p>
      </div>

      {/* Interpretation */}
      {result.interpretation && (
        <div
          className="animate-fade-in-up rounded-xl border border-zinc-100 bg-white p-6 shadow-sm"
          style={{ animationDelay: "100ms" }}
        >
          <InterpretationCard interpretation={result.interpretation} />
        </div>
      )}

      {/* SHAP Chart */}
      {result.shap?.contributions?.length ? (
        <div
          className="animate-fade-in-up rounded-xl border border-zinc-100 bg-white p-6 shadow-sm"
          style={{ animationDelay: "200ms" }}
        >
          <ShapChart contributions={result.shap.contributions} />
        </div>
      ) : null}
    </div>
  );
}
