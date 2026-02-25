import type {
  FeatureFormValues,
  FeatureSchema,
} from "@/app/config/features";

interface FeaturePanelProps {
  title: string;
  features: readonly FeatureSchema[];
  values: FeatureFormValues;
  onChange: (id: FeatureSchema["id"], nextValue: string) => void;
  onSubmit: () => void;
  isSubmitting: boolean;
  submitDisabled: boolean;
  errorMessage?: string | null;
}

export function FeaturePanel({
  title,
  features,
  values,
  onChange,
  onSubmit,
  isSubmitting,
  submitDisabled,
  errorMessage = null,
}: FeaturePanelProps) {
  return (
    <aside className="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:w-72">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{title}</p>
      <div className="mt-5 space-y-5">
        {features.map((feature) => (
          <label
            key={feature.id}
            htmlFor={feature.id}
            className="block space-y-2 rounded-lg border border-slate-100 bg-slate-50 px-3 py-3"
          >
            <span className="block text-sm font-medium text-slate-700">
              {feature.label}
            </span>
            {feature.type === "number" ? (
              <input
                id={feature.id}
                type="number"
                value={values[feature.id]}
                placeholder={feature.placeholder}
                onChange={(event) => onChange(feature.id, event.target.value)}
                className="block w-full rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-sm text-slate-700 tabular-nums focus:border-slate-400 focus:outline-none"
              />
            ) : (
              <select
                id={feature.id}
                value={values[feature.id]}
                onChange={(event) => onChange(feature.id, event.target.value)}
                className="block w-full rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-sm text-slate-700 focus:border-slate-400 focus:outline-none"
              >
                {feature.options.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            )}
            {"help" in feature && feature.help ? (
              <p className="text-xs text-slate-500">{feature.help}</p>
            ) : null}
          </label>
        ))}
      </div>
      <button
        type="button"
        onClick={onSubmit}
        disabled={isSubmitting || submitDisabled}
        className="mt-6 w-full rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSubmitting ? "Estimating..." : "Estimate"}
      </button>
      {errorMessage ? <p className="mt-3 text-xs font-medium text-rose-600">{errorMessage}</p> : null}
    </aside>
  );
}
