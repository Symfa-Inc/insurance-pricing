import type { ShapContribution } from "@/app/types/api";

interface ShapChartProps {
  contributions: ShapContribution[];
}

function formatValue(value: string | number): string {
  if (typeof value === "number") {
    return Number.isInteger(value) ? `${value}` : value.toFixed(1);
  }
  return value;
}

export function ShapChart({ contributions }: ShapChartProps) {
  if (contributions.length === 0) return null;

  const maxAbs = Math.max(
    ...contributions.map((c) => Math.abs(c.shap_value)),
    1e-9,
  );

  return (
    <section>
      <p className="text-xs font-medium uppercase tracking-wider text-zinc-400">
        Feature Impact
      </p>

      <ul className="mt-4 space-y-3.5">
        {contributions.map((item) => {
          const pct = Math.max(3, (Math.abs(item.shap_value) / maxAbs) * 100);
          const positive = item.shap_value >= 0;

          return (
            <li key={`${item.feature}-${item.value}`}>
              <div className="flex items-baseline justify-between gap-2 text-sm">
                <span className="font-medium text-zinc-700">
                  {item.feature}{" "}
                  <span className="font-normal text-zinc-400">
                    {formatValue(item.value)}
                  </span>
                </span>
                <span
                  className={`font-mono text-xs font-medium tabular-nums ${
                    positive ? "text-emerald-600" : "text-rose-500"
                  }`}
                >
                  {positive ? "+" : ""}
                  {item.shap_value.toFixed(0)}
                </span>
              </div>
              <div className="mt-1.5 h-1.5 rounded-full bg-zinc-100">
                <div
                  className={`h-1.5 rounded-full transition-all duration-700 ease-out ${
                    positive ? "bg-emerald-500" : "bg-rose-400"
                  }`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
