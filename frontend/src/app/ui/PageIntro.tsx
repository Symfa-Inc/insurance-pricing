export function PageIntro() {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Insurance Pricing</p>
      <h1 className="mt-2 text-3xl font-semibold text-slate-900">Insurance Charges Estimator</h1>
      <div className="mt-4 space-y-3 text-sm text-slate-500">
        <p>
          This app estimates annual insurance charges from profile inputs such as age, sex, BMI, number of
          children, smoker status, and region.
        </p>
        <p>
          It sends your submitted values to a demo machine learning model and returns a single dollar estimate,
          with optional interpretation and explainability details when available.
        </p>
        <p>
          Results are for product demonstration and model behavior exploration, and should not be treated as
          medical, legal, or financial advice.
        </p>
      </div>
    </section>
  );
}
