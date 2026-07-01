"use client";

import { useEffect, useState } from "react";

import Spinner from "@/components/Spinner";
import { displayUrl } from "@/lib/audit-format";
import type { JobStatus } from "@/lib/types";

export default function LoadingCard({
  url,
  status,
}: {
  url: string;
  status: JobStatus;
}) {
  const [showDelayNote, setShowDelayNote] = useState(false);
  const label =
    status === "running" ? "Analyzing page..." : "Starting audit...";

  useEffect(() => {
    setShowDelayNote(false);
    const timer = setTimeout(() => setShowDelayNote(true), 25000);
    return () => clearTimeout(timer);
  }, [url]);

  return (
    <div className="flex min-h-[360px] items-center">
      <div className="w-full rounded-2xl border border-line bg-surface p-6 text-center shadow-xl shadow-black/[0.04] sm:p-10">
        <div className="mx-auto max-w-lg">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary-soft text-primary">
            <Spinner className="h-6 w-6" />
          </div>
          <h2 className="mt-5 text-xl font-extrabold tracking-tight text-ink">
            {label}
          </h2>
          <p className="mt-2 break-words text-sm font-semibold text-primary-ink [overflow-wrap:anywhere]">
            {displayUrl(url)}
          </p>
          <p className="mt-4 text-sm leading-relaxed text-ink-2">
            {"We're gathering the page, metadata, links, and technical checks."}
          </p>
          {showDelayNote && (
            <p className="mt-3 text-xs font-medium text-ink-3">
              Larger pages can take a little longer...
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
