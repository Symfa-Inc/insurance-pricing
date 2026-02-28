import type { InterpretationPayload } from "@/app/types/api";
import { Tooltip } from "@/app/ui/Tooltip";

interface InterpretationCardProps {
  interpretation: InterpretationPayload;
}

export function InterpretationCard({ interpretation }: InterpretationCardProps) {
  return (
    <section>
      <div className="flex items-center gap-1.5">
        <p className="text-xs font-medium uppercase tracking-wider text-zinc-400">
          Interpretation
        </p>
        <Tooltip text="Highlights the primary factors and their influence on the estimated charges." />
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
