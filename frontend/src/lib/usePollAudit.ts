"use client";

import { useEffect, useRef, useState } from "react";

import { getAudit } from "./api";
import type { AuditJobResponse } from "./types";

export type AuditPhase = "loading" | "done" | "failed" | "error";

export interface PollResult {
  phase: AuditPhase;
  job: AuditJobResponse | null;
  error: string | null;
}

/**
 * Poll GET /api/audit/{jobId} until the job reaches a terminal state.
 * - pending/running -> keep polling ("loading")
 * - done            -> "done"
 * - failed          -> "failed" (with the backend error)
 * - fetch throws    -> "error"
 */
export function usePollAudit(jobId: string | null, intervalMs = 1500): PollResult {
  const [job, setJob] = useState<AuditJobResponse | null>(null);
  const [phase, setPhase] = useState<AuditPhase>("loading");
  const [error, setError] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (!jobId) return;

    let cancelled = false;
    setPhase("loading");
    setJob(null);
    setError(null);

    async function tick() {
      try {
        const next = await getAudit(jobId as string);
        if (cancelled) return;

        setJob(next);

        if (next.status === "done") {
          setPhase("done");
          return;
        }
        if (next.status === "failed") {
          setError(next.error ?? "The audit failed.");
          setPhase("failed");
          return;
        }
        // pending / running -> poll again
        timer.current = setTimeout(tick, intervalMs);
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Failed to fetch results.");
        setPhase("error");
      }
    }

    tick();

    return () => {
      cancelled = true;
      if (timer.current) clearTimeout(timer.current);
    };
  }, [jobId, intervalMs]);

  return { phase, job, error };
}
