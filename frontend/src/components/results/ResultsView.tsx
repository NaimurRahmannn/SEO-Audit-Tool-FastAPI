"use client";

import { usePollAudit } from "@/lib/usePollAudit";
import AuditReport from "./AuditReport";
import ErrorCard from "./ErrorCard";
import LoadingCard from "./LoadingCard";

interface ResultsViewProps {
  jobId: string;
  url: string;
  onReset: () => void;
  onRerun: () => void;
  rerunning: boolean;
}

export default function ResultsView({
  jobId,
  url,
  onReset,
  onRerun,
  rerunning,
}: ResultsViewProps) {
  const { phase, job, error } = usePollAudit(jobId);

  if (phase === "loading") {
    return <LoadingCard url={url} status={job?.status ?? "pending"} />;
  }

  if (phase === "failed" || phase === "error") {
    return <ErrorCard message={error ?? "The audit failed."} onReset={onReset} />;
  }

  const result = job?.result;
  if (!result) {
    return (
      <ErrorCard
        message="The audit finished but returned no result."
        onReset={onReset}
      />
    );
  }

  return (
    <AuditReport
      result={result}
      requestedUrl={url}
      onRerun={onRerun}
      rerunning={rerunning}
    />
  );
}
