"use client";

import { useRef, useState } from "react";
import type { FormEvent } from "react";

import { startAudit } from "@/lib/api";
import Spinner from "@/components/Spinner";
import { ArrowRightIcon, GlobeIcon } from "@/components/icons";
import { toReadableErrorMessage } from "@/lib/error-copy";

const EXAMPLES = ["stripe.com", "airbnb.com", "github.com"];

interface SearchCardProps {
  /** Called with the new job id (and normalized url) after a successful start. */
  onStarted: (jobId: string, url: string) => void;
}

export default function SearchCard({ onStarted }: SearchCardProps) {
  const [url, setUrl] = useState("");
  const [checkBrokenLinks, setCheckBrokenLinks] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [validationMessage, setValidationMessage] = useState<string | null>(
    null
  );
  const [submitError, setSubmitError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const describedBy = [
    validationMessage ? "audit-url-validation" : null,
    submitError ? "audit-url-submit-error" : null,
  ]
    .filter(Boolean)
    .join(" ");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationMessage(null);
    setSubmitError(null);

    const trimmed = url.trim();
    if (!trimmed) {
      setValidationMessage("Enter a URL to audit.");
      return;
    }

    setSubmitting(true);
    try {
      // Scheme is optional — the backend normalizes it.
      const job = await startAudit(trimmed, checkBrokenLinks);
      onStarted(job.id, job.url);
    } catch (err) {
      setSubmitError(
        toReadableErrorMessage(
          err,
          "We couldn't start the audit. Please try again."
        )
      );
    } finally {
      setSubmitting(false);
    }
  }

  function applyExample(example: string) {
    setUrl(example);
    setValidationMessage(null);
    setSubmitError(null);
    inputRef.current?.focus();
  }

  return (
    <div>
      <div className="rounded-[18px] bg-surface p-3 shadow-xl shadow-black/[0.06] ring-1 ring-line sm:p-4">
        <form onSubmit={handleSubmit} noValidate>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-3 px-2 sm:px-3">
                <GlobeIcon className="h-5 w-5 shrink-0 text-ink-3" />
                <label htmlFor="audit-url" className="sr-only">
                  Website URL
                </label>
                <input
                  id="audit-url"
                  ref={inputRef}
                  name="url"
                  type="text"
                  inputMode="url"
                  autoComplete="url"
                  placeholder="https://example.com"
                  value={url}
                  onChange={(e) => {
                    setUrl(e.target.value);
                    setValidationMessage(null);
                    setSubmitError(null);
                  }}
                  disabled={submitting}
                  aria-invalid={validationMessage ? true : undefined}
                  aria-describedby={describedBy || undefined}
                  className="w-full bg-transparent py-3 text-lg text-ink placeholder:text-ink-3 focus:outline-none disabled:opacity-60"
                />
              </div>

              {validationMessage && (
                <p
                  id="audit-url-validation"
                  role="alert"
                  className="px-10 pb-1 text-sm font-medium text-ink-3 sm:px-11"
                >
                  {validationMessage}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3.5 text-base font-bold text-white transition-colors hover:bg-primary-ink focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {submitting ? (
                <>
                  <Spinner />
                  Starting…
                </>
              ) : (
                <>
                  <ArrowRightIcon className="h-5 w-5" />
                  Run audit
                </>
              )}
            </button>
          </div>

          <div className="mt-2 flex justify-center">
            <label className="flex cursor-pointer items-center gap-2 py-1 text-sm text-ink-2">
              <input
                type="checkbox"
                checked={checkBrokenLinks}
                onChange={(e) => setCheckBrokenLinks(e.target.checked)}
                disabled={submitting}
                className="h-4 w-4 rounded border-line text-primary focus:ring-primary"
              />
              Also check for broken links{" "}
              <span className="text-ink-3">(slower)</span>
            </label>
          </div>
        </form>
      </div>

      {submitError && (
        <p
          id="audit-url-submit-error"
          role="alert"
          className="mx-auto mt-3 w-fit rounded-lg bg-fail-bg px-3 py-2 text-center text-sm font-medium text-fail-ink"
        >
          {submitError}
        </p>
      )}

      <div className="mt-5 flex flex-wrap items-center justify-center gap-2 text-sm">
        <span className="text-ink-2">Try an example:</span>
        {EXAMPLES.map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => applyExample(example)}
            className="rounded-lg bg-primary-soft px-3 py-1.5 font-semibold text-primary-ink transition-colors hover:bg-primary hover:text-white"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}
