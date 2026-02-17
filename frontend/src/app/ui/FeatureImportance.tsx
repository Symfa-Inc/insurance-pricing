import type { FeatureImportanceItem } from "@/app/types/api";

interface FeatureImportanceProps {
  items?: FeatureImportanceItem[];
}

export function FeatureImportance({ items }: FeatureImportanceProps) {
  const hasItems = Boolean(items && items.length > 0);

  return (
    <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-zinc-900">What influenced the estimate</h2>
      {hasItems ? (
        <ul className="mt-4 space-y-3">
          {items?.map((item) => (
            <li key={item.name} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-700">{item.name}</span>
                <span className="font-medium text-zinc-900">{item.value.toFixed(3)}</span>
              </div>
              <div className="h-2 rounded-full bg-zinc-100">
                <div
                  className="h-2 rounded-full bg-zinc-700"
                  style={{ width: `${Math.max(4, Math.min(100, item.value * 100))}%` }}
                />
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-4 text-sm leading-6 text-zinc-600">
          Feature importance not available for this model yet.
        </p>
      )}
    </section>
  );
}
