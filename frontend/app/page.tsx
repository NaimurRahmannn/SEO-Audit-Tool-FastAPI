"use client";

import { useCallback, useState } from "react";

import ChecklistGrid from "@/components/ChecklistGrid";
import FeatureCards from "@/components/FeatureCards";
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import SearchCard from "@/components/SearchCard";
import { PlusIcon } from "@/components/icons";
import ResultsView from "@/components/results/ResultsView";
import { startAudit } from "@/lib/api";

interface StartedJob {
  id: string;
  url: string;
}

export default function Home() {
  const [job, setJob] = useState<StartedJob | null>(null);
  const [rerunning, setRerunning] = useState(false);

  const reset = useCallback(() => {
    setJob(null);
    setRerunning(false);
  }, []);

  const rerun = useCallback(async () => {
    if (!job) return;
    setRerunning(true);
    try {
      const next = await startAudit(job.url, false);
      setJob({ id: next.id, url: job.url });
    } catch {
      // Keep showing the current report if re-running fails to start.
    } finally {
      setRerunning(false);
    }
  }, [job]);

  // Results view (loading / done / error) once a job exists.
  if (job) {
    return (
      <>
        <Header>
          <button
            type="button"
            onClick={reset}
            className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-3.5 py-2 text-sm font-bold text-white transition-colors hover:bg-primary-ink"
          >
            <PlusIcon className="h-4 w-4" />
            New audit
          </button>
        </Header>
        <main className="mx-auto w-full max-w-4xl px-6 pb-24 pt-10">
          <ResultsView
            key={job.id}
            jobId={job.id}
            url={job.url}
            onReset={reset}
            onRerun={rerun}
            rerunning={rerunning}
          />
        </main>
      </>
    );
  }

  // Landing view.
  return (
    <>
      <Header />
      <main className="mx-auto w-full max-w-6xl px-6 pb-20 pt-14 sm:pt-20">
        <Hero />

        <div className="mx-auto mt-10 max-w-4xl">
          <SearchCard onStarted={(id, url) => setJob({ id, url })} />
        </div>

        <div className="mt-16">
          <FeatureCards />
        </div>

        <div className="mt-6">
          <ChecklistGrid />
        </div>
      </main>
    </>
  );
}
