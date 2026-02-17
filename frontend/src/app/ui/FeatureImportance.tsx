import type { FeatureImportanceItem } from "@/app/types/api";

interface FeatureImportanceProps {
  items?: FeatureImportanceItem[];
}

export function FeatureImportance({ items }: FeatureImportanceProps) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
          Explainability
        </p>
        <h3 className="text-2xl font-semibold text-slate-900">What influenced the estimate</h3>
      </div>
      <ul className="mt-6 space-y-4">
        {items?.map((item) => (
          <li key={item.name} className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-slate-700">{item.name}</span>
              <span className="text-slate-500">{item.value.toFixed(2)}</span>
            </div>
            <div className="h-3 rounded-full bg-slate-100">
              <div
                className="h-3 rounded-full bg-gradient-to-r from-indigo-500 via-sky-500 to-emerald-400"
                style={{ width: `${item.value * 100}%` }}
              />
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
