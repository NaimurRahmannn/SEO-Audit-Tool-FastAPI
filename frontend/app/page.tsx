"use client";

import { useState } from "react";

import ChecklistGrid from "@/components/ChecklistGrid";
import FeatureCards from "@/components/FeatureCards";
import Hero from "@/components/Hero";
import SearchCard from "@/components/SearchCard";

interface StartedJob {
  id: string;
  url: string;
}

export default function Home() {
  const [job, setJob] = useState<StartedJob | null>(null);

  return (
    <main className="mx-auto w-full max-w-6xl px-6 pb-20 pt-14 sm:pt-20">
      <Hero />

      <div className="mx-auto mt-10 max-w-4xl">
        <SearchCard onStarted={(id, url) => setJob({ id, url })} />

        {/* Placeholder handoff — live polling and the results view come next. */}
        {job && (
          <section className="mx-auto mt-5 max-w-2xl rounded-2xl border border-line bg-surface p-5">
            <p className="text-sm text-ink-2">
              Audit started for{" "}
              <span className="font-semibold text-ink">{job.url}</span>
            </p>
            <p className="mt-1 text-sm text-ink-3">
              Job{" "}
              <code className="rounded bg-soft px-1.5 py-0.5 font-mono text-xs text-ink-2">
                {job.id}
              </code>{" "}
              (status: pending)
            </p>
          </section>
        )}
      </div>

      <div className="mt-16">
        <FeatureCards />
      </div>

      <div className="mt-6">
        <ChecklistGrid />
      </div>
    </main>
  );
}
