export function formatCurrencyUSD(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(value);
}

export interface SummaryAuxField {
  label: string;
  value: string;
}

interface StatusSummaryProps {
  headline: string;
  summary: string;
  value?: number;
  unit?: string;
  auxFields?: SummaryAuxField[];
  isLoading?: boolean;
  errorMessage?: string | null;
}

function formatValue(value: number, unit?: string): string {
  if (unit === "$" || !unit) {
    return formatCurrencyUSD(value);
  }

  return `${unit}${value.toFixed(2)}`;
}

export function StatusSummary({
  headline,
  summary,
  value,
  unit,
  auxFields,
  isLoading = false,
  errorMessage = null,
}: StatusSummaryProps) {
  return (
    <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
      <p className="text-sm font-medium text-zinc-500">{headline}</p>
      <p className="mt-3 text-4xl font-semibold tracking-tight text-zinc-900">
        {typeof value === "number" ? formatValue(value, unit) : "--"}
      </p>
      <p className="mt-3 text-sm leading-6 text-zinc-600">{summary}</p>

      {isLoading ? (
        <p className="mt-4 text-sm text-zinc-500">Refreshing estimate...</p>
      ) : null}

      {errorMessage ? (
        <p className="mt-4 rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          {errorMessage}
        </p>
      ) : null}

      {auxFields?.length ? (
        <dl className="mt-4 space-y-1 text-sm text-zinc-500">
          {auxFields.map((field) => (
            <div key={field.label} className="flex items-center justify-between gap-2">
              <dt>{field.label}</dt>
              <dd className="font-medium text-zinc-700">{field.value}</dd>
            </div>
          ))}
        </dl>
      ) : null}
    </section>
  );
}
