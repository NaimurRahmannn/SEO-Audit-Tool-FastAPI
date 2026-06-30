"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { startAudit } from "@/lib/api";
import Spinner from "@/components/Spinner";

interface AuditFormProps {
  /** Called with the new job id (and the normalized url) after a successful start. */
  onStarted: (jobId: string, url: string) => void;
}

export default function AuditForm({ onStarted }: AuditFormProps) {
  const [url, setUrl] = useState("");
  const [checkBrokenLinks, setCheckBrokenLinks] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const trimmed = url.trim();
    if (!trimmed) {
      setError("Please enter a URL to audit.");
      return;
    }

    setSubmitting(true);
    try {
      // Scheme is optional — the backend normalizes it.
      const job = await startAudit(trimmed, checkBrokenLinks);
      onStarted(job.id, job.url);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="rounded-xl border border-hairline bg-surface p-6 shadow-sm"
    >
      <label
        htmlFor="audit-url"
        className="block text-sm font-medium text-slate-700"
      >
        Page URL
      </label>

      <div className="mt-2 flex flex-col gap-3 sm:flex-row">
        <input
          id="audit-url"
          name="url"
          type="text"
          inputMode="url"
          autoComplete="url"
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={submitting}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? "audit-url-error" : undefined}
          className="flex-1 rounded-lg border border-hairline bg-white px-4 py-2.5 text-base text-slate-900 placeholder:text-slate-400 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent disabled:opacity-60"
        />

        <button
          type="submit"
          disabled={submitting}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-accent px-5 py-2.5 text-base font-medium text-white transition-colors hover:bg-accent-hover focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? (
            <>
              <Spinner />
              Starting…
            </>
          ) : (
            "Run Audit"
          )}
        </button>
      </div>

      <label className="mt-4 flex items-center gap-2 text-sm text-slate-600">
        <input
          type="checkbox"
          checked={checkBrokenLinks}
          onChange={(e) => setCheckBrokenLinks(e.target.checked)}
          disabled={submitting}
          className="h-4 w-4 rounded border-hairline text-accent focus:ring-accent"
        />
        Also check for broken links (slower)
      </label>

      {error && (
        <p
          id="audit-url-error"
          role="alert"
          className="mt-4 rounded-lg bg-fail-bg px-3 py-2 text-sm text-fail"
        >
          {error}
        </p>
      )}
    </form>
  );
}
