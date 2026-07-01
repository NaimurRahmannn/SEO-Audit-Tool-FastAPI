import type { ComponentType } from "react";

import {
  CheckTickIcon,
  ClockIcon,
  ListIcon,
  PhoneIcon,
  RerunIcon,
} from "@/components/icons";
import { displayUrl, relativeTime, statusLabel } from "@/lib/audit-format";
import type { AuditResult } from "@/lib/types";

interface UrlBarProps {
  result: AuditResult;
  requestedUrl: string;
  onRerun: () => void;
  rerunning: boolean;
}

export default function UrlBar({ result, requestedUrl, onRerun, rerunning }: UrlBarProps) {
  const url = displayUrl(result.final_url ?? requestedUrl);

  const chips: { Icon: ComponentType<{ className?: string }>; label: string }[] = [
    { Icon: ClockIcon, label: relativeTime(result.fetched_at) },
    { Icon: PhoneIcon, label: "mobile" },
    { Icon: CheckTickIcon, label: statusLabel(result.status_code) },
    { Icon: ListIcon, label: `${result.checks.length} checks` },
  ];

  return (
    <div className="flex flex-wrap items-start justify-between gap-4">
      <div className="min-w-0">
        <p className="text-xs font-bold uppercase tracking-wider text-primary">
          Audit Report
        </p>
        <h1 className="mt-1 break-all text-2xl font-extrabold tracking-tight text-ink sm:text-3xl">
          {url}
        </h1>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          {chips.map(({ Icon, label }) => (
            <span
              key={label}
              className="inline-flex items-center gap-1.5 rounded-full border border-line bg-surface px-2.5 py-1 text-xs font-medium text-ink-2"
            >
              <Icon className="h-3.5 w-3.5 text-ink-3" />
              {label}
            </span>
          ))}
        </div>
      </div>

      <button
        type="button"
        onClick={onRerun}
        disabled={rerunning}
        className="inline-flex shrink-0 items-center gap-2 rounded-lg border border-line bg-surface px-3.5 py-2 text-sm font-semibold text-ink-2 transition-colors hover:bg-soft disabled:opacity-60"
      >
        <RerunIcon className="h-4 w-4" />
        {rerunning ? "Re-running…" : "Re-run"}
      </button>
    </div>
  );
}
