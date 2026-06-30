"use client";

import { useState } from "react";

import AuditForm from "@/components/AuditForm";

interface StartedJob {
  id: string;
  url: string;
}

export default function Home() {
  const [job, setJob] = useState<StartedJob | null>(null);

  return (
    <div className="space-y-8">
      <section className="space-y-2">
        <h2 className="text-2xl font-semibold tracking-tight text-slate-900">
          Audit a page
        </h2>
        <p className="text-sm text-slate-500">
          Enter a URL to analyze its title, meta tags, headings, images, links,
          social cards, structured data, and more.
        </p>
      </section>

      <AuditForm onStarted={(id, url) => setJob({ id, url })} />

      {/* Placeholder handoff — real polling and results come next. */}
      {job && (
        <section className="rounded-xl border border-hairline bg-surface p-5 shadow-sm">
          <p className="text-sm text-slate-600">
            Audit started for{" "}
            <span className="font-medium text-slate-900">{job.url}</span>
          </p>
          <p className="mt-1 text-sm text-slate-500">
            Job{" "}
            <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs text-slate-700">
              {job.id}
            </code>{" "}
            (status: pending)
          </p>
        </section>
      )}
    </div>
  );
}
