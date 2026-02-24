import type { ShapContribution } from "@/app/types/api";

interface ShapChartProps {
  contributions: ShapContribution[];
  embedded?: boolean;
  baseValue?: number;
  predictedValue?: number;
}

function formatFeatureValue(value: string | number): string {
  if (typeof value === "number") {
    return Number.isInteger(value) ? `${value}` : value.toFixed(2);
  }
  return value;
}

export function ShapChart({
  contributions,
  embedded = false,
  baseValue,
  predictedValue,
}: ShapChartProps) {
  if (contributions.length === 0) {
    return null;
  }

  const sumImpacts = contributions.reduce((sum, item) => sum + item.shap_value, 0);
  const maxAbs = Math.max(...contributions.map((item) => Math.abs(item.shap_value)), 1e-9);
  const containerClass = embedded ? "" : "rounded-2xl border border-slate-200 bg-white p-8 shadow-sm";

  return (
    <section className={containerClass}>
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Explainability</p>
        <h3 className="text-2xl font-semibold text-slate-900">What influenced the estimate</h3>
      </div>
      <p className="mt-4 text-sm text-slate-600">
        Feature impacts are centered at zero. Positive values increase the estimate; negative values decrease it.
      </p>

      <ul className="mt-6 space-y-4">
        {contributions.map((item) => {
          const widthPercent = Math.max(3, (Math.abs(item.shap_value) / maxAbs) * 50);
          const isPositive = item.shap_value >= 0;
          const valueTextClass = isPositive ? "font-semibold text-indigo-600" : "font-semibold text-rose-600";
          const barClass = isPositive ? "left-1/2 bg-indigo-500" : "right-1/2 bg-rose-500";

          return (
            <li key={`${item.feature}-${item.value}`} className="space-y-2">
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-medium text-slate-700">
                  {item.feature} = {formatFeatureValue(item.value)}
                </span>
                <span className={`tabular-nums ${valueTextClass}`}>
                  {item.shap_value >= 0 ? "+" : ""}
                  {item.shap_value.toFixed(2)} {isPositive ? "↑" : "↓"}
                </span>
              </div>
              <div className="relative flex h-6 items-center">
                <div className="absolute left-1/2 h-4 w-px -translate-x-px bg-slate-300" />
                <div
                  className={`absolute top-1/2 h-4 -translate-y-1/2 rounded ${barClass}`}
                  style={{
                    width: `${widthPercent}%`,
                    ...(isPositive ? { left: "50%" } : { right: "50%" }),
                  }}
                />
              </div>
            </li>
          );
        })}
      </ul>

      {baseValue !== undefined && predictedValue !== undefined ? (
        <div className="mt-5 rounded-lg border border-indigo-200 bg-indigo-50 px-4 py-3">
          <p className="text-sm font-medium text-slate-700">
            <span className="tabular-nums">{baseValue.toFixed(2)}</span> baseline +{" "}
            <span className="tabular-nums">{sumImpacts.toFixed(2)}</span> (from features) ={" "}
            <strong className="tabular-nums text-indigo-700">{predictedValue.toFixed(2)} estimate</strong>
          </p>
        </div>
      ) : null}
      <p className="mt-3 text-xs text-slate-500">Positive (indigo) pushes the estimate up; negative (rose) pulls it down.</p>
    </section>
  );
}
