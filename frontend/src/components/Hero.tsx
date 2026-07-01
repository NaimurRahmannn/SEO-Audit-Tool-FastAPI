export default function Hero() {
  return (
    <section className="text-center">
      <span className="inline-flex items-center gap-2 rounded-full bg-primary-soft px-3.5 py-1.5 text-sm font-semibold text-primary-ink">
        <span className="h-1.5 w-1.5 rounded-full bg-primary" aria-hidden="true" />
        Free instant SEO analysis
      </span>

      <h1 className="mx-auto mt-6 max-w-3xl text-5xl font-extrabold leading-[1.05] tracking-tight text-ink sm:text-6xl">
        Audit any website&apos;s
        <span className="block text-primary">SEO in seconds</span>
      </h1>

      <p className="mx-auto mt-6 max-w-2xl text-lg text-ink-2 sm:text-xl">
        Enter a URL and get a clear, actionable report across 20+ checks — with
        exact fixes for every issue.
      </p>
    </section>
  );
}
