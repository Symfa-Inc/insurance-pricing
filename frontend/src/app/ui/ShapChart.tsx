import type { ShapContribution } from "@/app/types/api";
import { Tooltip } from "@/app/ui/Tooltip";

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
      <div className="flex items-center gap-1.5">
        <p className="text-xs font-medium uppercase tracking-wider text-zinc-400">
          Feature Impact
        </p>
        <Tooltip text="Shows how each input pushed the estimate higher or lower relative to the average." />
      </div>

      <ul className="mt-4 space-y-3">
        {contributions.map((item) => {
          const widthPct = Math.max(
            2,
            (Math.abs(item.shap_value) / maxAbs) * 45,
          );
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
              <div className="relative mt-1.5 h-2 rounded-full bg-zinc-100">
                <div className="absolute inset-y-0 left-1/2 w-px -translate-x-1/2 bg-zinc-300" />
                <div
                  className={`absolute inset-y-0 transition-all duration-700 ease-out ${
                    positive
                      ? "left-1/2 rounded-r-full bg-emerald-500"
                      : "right-1/2 rounded-l-full bg-rose-400"
                  }`}
                  style={{ width: `${widthPct}%` }}
                />
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
