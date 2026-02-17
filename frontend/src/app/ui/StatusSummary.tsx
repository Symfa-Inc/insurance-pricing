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
  value: number | null;
  modelVersion?: string;
}

export function StatusSummary({
  headline,
  summary,
  value,
  modelVersion,
}: StatusSummaryProps) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{headline}</p>
          <h2 className="text-2xl font-semibold text-slate-900">Pricing estimate</h2>
          <p className="text-sm text-slate-500">{summary}</p>
          {modelVersion ? <p className="text-sm text-slate-500">Model version: {modelVersion}</p> : null}
        </div>
        <div className="rounded-2xl border border-indigo-100 bg-indigo-50 px-6 py-4 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-400">Estimated Charges</p>
          <p className="mt-2 text-3xl font-semibold text-indigo-600">
            {typeof value === "number" ? formatCurrencyUSD(value) : "--"}
          </p>
        </div>
      </div>
    </section>
  );
}
