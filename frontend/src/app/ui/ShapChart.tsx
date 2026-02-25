import type { ShapContribution } from "@/app/types/api";

interface ShapChartProps {
  contributions: ShapContribution[];
  embedded?: boolean;
}

function formatFeatureValue(value: string | number): string {
  if (typeof value === "number") {
    return Number.isInteger(value) ? `${value}` : value.toFixed(2);
  }
  return value;
}

export function ShapChart({ contributions, embedded = false }: ShapChartProps) {
  if (contributions.length === 0) {
    return null;
  }

  const maxAbs = Math.max(...contributions.map((item) => Math.abs(item.shap_value)), 1e-9);
  const containerClass = embedded ? "" : "rounded-2xl border border-slate-200 bg-white p-8 shadow-sm";

  return (
    <section className={containerClass}>
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Explainability</p>
        <h3 className="text-2xl font-semibold text-slate-900">What influenced the estimate</h3>
      </div>

      <ul className="mt-6 space-y-4">
        {contributions.map((item) => {
          const widthPercent = Math.max(1.5, (Math.abs(item.shap_value) / maxAbs) * 50);
          const isPositive = item.shap_value >= 0;
          const tone = isPositive
            ? "bg-gradient-to-r from-indigo-500 to-indigo-300 text-indigo-700"
            : "bg-gradient-to-l from-rose-500 to-rose-300 text-rose-700";
          const directionLabel = isPositive ? "adds to estimate" : "reduces estimate";

          return (
            <li key={`${item.feature}-${item.value}`} className="space-y-2">
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-medium text-slate-700">
                  {item.feature} = {formatFeatureValue(item.value)}
                </span>
                <span className={`text-xs ${isPositive ? "text-indigo-600" : "text-rose-600"}`}>
                  {isPositive ? "+" : "-"}
                  {Math.abs(item.shap_value).toFixed(2)} ({directionLabel})
                </span>
              </div>
              <div className="relative h-5 overflow-hidden rounded-full bg-slate-100">
                <div className="absolute inset-y-0 left-1/2 w-px -translate-x-1/2 bg-slate-300" />
                <div
                  className={`absolute inset-y-0 ${tone} ${
                    isPositive ? "left-1/2 rounded-r-full" : "right-1/2 rounded-l-full"
                  }`}
                  style={{ width: `${widthPercent}%` }}
                />
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
