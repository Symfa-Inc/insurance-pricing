import type { InterpretationPayload } from "@/app/types/api";

interface InterpretationCardProps {
  interpretation: InterpretationPayload;
  embedded?: boolean;
}

export function InterpretationCard({ interpretation, embedded = false }: InterpretationCardProps) {
  const containerClass = embedded ? "" : "rounded-2xl border border-slate-200 bg-white p-8 shadow-sm";
  return (
    <section className={containerClass}>
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Interpretation</p>
      <h3 className="mt-3 text-2xl font-semibold text-slate-900">{interpretation.headline}</h3>

      <ul className="mt-4 list-disc space-y-2 pl-5">
        {interpretation.bullets.map((bullet) => (
          <li key={bullet} className="text-sm text-slate-600">
            {bullet}
          </li>
        ))}
      </ul>

      <div className="mt-5">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Caveats</p>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          {interpretation.caveats.map((caveat) => (
            <li key={caveat} className="text-xs text-slate-400">
              {caveat}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
