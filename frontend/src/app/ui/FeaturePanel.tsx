import { useEffect, useRef } from "react";
import type { FeatureFormValues, FeatureSchema } from "@/app/config/features";

interface FeaturePanelProps {
  features: readonly FeatureSchema[];
  values: FeatureFormValues;
  onChange: (id: FeatureSchema["id"], nextValue: string) => void;
  onSubmit: () => void;
  isSubmitting: boolean;
  submitDisabled: boolean;
}

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function FeaturePanel({
  features,
  values,
  onChange,
  onSubmit,
  isSubmitting,
  submitDisabled,
}: FeaturePanelProps) {
  const formRef = useRef<HTMLDivElement>(null);

  /* Scroll wheel adjusts number inputs without scrolling the page */
  useEffect(() => {
    const el = formRef.current;
    if (!el) return;

    const handler = (e: WheelEvent) => {
      const input = (e.target as HTMLElement).closest(
        'input[type="number"]',
      ) as HTMLInputElement | null;
      if (!input) return;
      e.preventDefault();

      const id = input.id as FeatureSchema["id"];
      const step = parseFloat(input.step) || 1;
      const min = input.min !== "" ? parseFloat(input.min) : -Infinity;
      const max = input.max !== "" ? parseFloat(input.max) : Infinity;
      const current = parseFloat(input.value) || 0;
      const direction = e.deltaY < 0 ? 1 : -1;
      const decimals = Math.max((input.step.split(".")[1] || "").length, 0);
      const next = Math.min(
        max,
        Math.max(min, parseFloat((current + direction * step).toFixed(decimals))),
      );

      onChange(id, String(next));
    };

    el.addEventListener("wheel", handler, { passive: false });
    return () => el.removeEventListener("wheel", handler);
  }, [onChange]);

  return (
    <div ref={formRef} className="space-y-5">
      <div className="space-y-4">
        {features.map((feature) => (
          <div key={feature.id} className="space-y-1.5">
            <label
              htmlFor={feature.id}
              className="block text-xs font-medium text-zinc-500"
            >
              {feature.label}
            </label>
            {feature.type === "number" ? (
              <input
                id={feature.id}
                type="number"
                value={values[feature.id]}
                placeholder={feature.placeholder}
                step={feature.step}
                min={feature.min}
                max={feature.max}
                onChange={(e) => onChange(feature.id, e.target.value)}
                className="block w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 placeholder:text-zinc-300 transition-colors focus:border-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-900"
              />
            ) : (
              <div className="overflow-hidden rounded-lg border border-zinc-200 bg-white transition-colors focus-within:border-zinc-900 focus-within:ring-1 focus-within:ring-zinc-900">
                <select
                  id={feature.id}
                  value={values[feature.id]}
                  onChange={(e) => onChange(feature.id, e.target.value)}
                  className="field block w-full rounded-none border-none bg-transparent px-3 py-2 text-sm text-zinc-900 focus:outline-none"
                >
                  {feature.options.map((option) => (
                    <option key={option} value={option}>
                      {capitalize(option)}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={onSubmit}
        disabled={isSubmitting || submitDisabled}
        className="w-full rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-zinc-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40"
      >
        {isSubmitting ? (
          <span className="flex items-center justify-center gap-2">
            <svg
              className="h-4 w-4 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="2.5"
                className="opacity-20"
              />
              <path
                d="M12 2a10 10 0 0 1 10 10"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
            </svg>
            Estimating
          </span>
        ) : (
          "Estimate"
        )}
      </button>
    </div>
  );
}
