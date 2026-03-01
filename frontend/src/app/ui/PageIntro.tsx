export function PageIntro() {
  return (
    <header>
      <div className="flex gap-3">
        <div className="w-1 shrink-0 rounded-full bg-emerald-400" />
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
            Insurance Pricing
          </h1>
          <p className="mt-1 text-sm text-zinc-500">
            Estimate insurance costs with ML-powered predictions and explainable
            AI insights
          </p>
        </div>
      </div>
      <div className="mt-4 h-px bg-gradient-to-r from-transparent via-zinc-200 to-transparent" />
    </header>
  );
}
