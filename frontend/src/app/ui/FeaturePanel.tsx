import type {
  CategoricalFeatureDefinition,
  FeatureDefinition,
  NumericFeatureDefinition,
} from "@/app/config/features";

interface FeaturePanelProps {
  feature: FeatureDefinition;
  value: string | number;
  onChange: (nextValue: string | number) => void;
}

function NumericField({
  feature,
  value,
  onChange,
}: {
  feature: NumericFeatureDefinition;
  value: number;
  onChange: (nextValue: number) => void;
}) {
  return (
    <input
      id={feature.key}
      type="number"
      value={value}
      min={feature.min}
      max={feature.max}
      step={feature.step}
      onChange={(event) => onChange(Number(event.target.value))}
      className="mt-2 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm outline-none transition focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500"
    />
  );
}

function CategoricalField({
  feature,
  value,
  onChange,
}: {
  feature: CategoricalFeatureDefinition;
  value: string;
  onChange: (nextValue: string) => void;
}) {
  return (
    <select
      id={feature.key}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className="mt-2 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm outline-none transition focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500"
    >
      {feature.options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  );
}

export function FeaturePanel({ feature, value, onChange }: FeaturePanelProps) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
      <label htmlFor={feature.key} className="block text-sm font-medium text-zinc-900">
        {feature.label}
      </label>
      {feature.description ? (
        <p className="mt-1 text-xs text-zinc-500">{feature.description}</p>
      ) : null}
      {feature.type === "numeric" ? (
        <NumericField
          feature={feature}
          value={Number(value)}
          onChange={(nextValue) => onChange(nextValue)}
        />
      ) : (
        <CategoricalField
          feature={feature}
          value={String(value)}
          onChange={(nextValue) => onChange(nextValue)}
        />
      )}
    </div>
  );
}
