import type { InterpretationPayload } from "@/app/types/api";

interface InterpretationCardProps {
  interpretation: InterpretationPayload;
}

export function InterpretationCard({ interpretation }: InterpretationCardProps) {
  return (
    <section>
      <p className="text-xs font-medium uppercase tracking-wider text-zinc-400">
        Interpretation
      </p>
      <h3 className="mt-2 text-base font-semibold text-zinc-900">
        {interpretation.headline}
      </h3>
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
