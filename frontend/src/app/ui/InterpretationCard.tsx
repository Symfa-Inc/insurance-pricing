import type { InterpretationPayload, InterpretationSource } from "@/app/types/api";
import { Tooltip } from "@/app/ui/Tooltip";

interface InterpretationCardProps {
  interpretation: InterpretationPayload;
  source: InterpretationSource;
}

function sourceBadgeClass(source: InterpretationSource): string {
  if (source === "fallback") {
    return "border-amber-200 bg-amber-50 text-amber-700";
  }

  return "border-emerald-200 bg-emerald-50 text-emerald-700";
}

export function InterpretationCard({ interpretation, source }: InterpretationCardProps) {
  const sourceLabel = source.toUpperCase();

  return (
    <section>
      <div className="flex items-center gap-1.5">
        <p className="text-xs font-medium uppercase tracking-wider text-zinc-400">
          Interpretation
        </p>
        <Tooltip text="Highlights the primary factors and their influence on the estimated charges." />
        <span
          className={`ml-1 inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold tracking-wide ${sourceBadgeClass(source)}`}
        >
          {sourceLabel}
        </span>
      </div>
      <ul className="mt-3 space-y-2">
        {interpretation.bullets.map((bullet) => (
          <li key={bullet} className="flex gap-2.5 text-sm leading-relaxed text-zinc-600">
            <span className="mt-2 h-1 w-1 flex-none rounded-full bg-zinc-300" />
            <span>{bullet}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
