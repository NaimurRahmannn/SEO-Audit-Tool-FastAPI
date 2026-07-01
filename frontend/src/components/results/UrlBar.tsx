import type { ComponentType } from "react";

import {
  CheckTickIcon,
  ClockIcon,
  ListIcon,
  PhoneIcon,
  RerunIcon,
  TriangleAlertIcon,
} from "@/components/icons";
import { displayUrl, relativeTime, statusLabel } from "@/lib/audit-format";
import type { AuditResult } from "@/lib/types";

interface UrlBarProps {
  result: AuditResult;
  requestedUrl: string;
  onRerun: () => void;
  rerunning: boolean;
}

const NEUTRAL_CHIP = "border-line bg-surface text-ink-2";
const NEUTRAL_ICON = "text-ink-3";

function statusTone(statusCode: number | null) {
  if (statusCode == null) {
    return {
      chipClassName: NEUTRAL_CHIP,
      iconClassName: NEUTRAL_ICON,
      Icon: CheckTickIcon,
    };
  }

  if (statusCode >= 400) {
    return {
      chipClassName: "border-fail-bg bg-fail-bg text-fail-ink",
      iconClassName: "text-fail",
      Icon: TriangleAlertIcon,
    };
  }

  if (statusCode >= 300) {
    return {
      chipClassName: "border-warn-bg bg-warn-bg text-warn-ink",
      iconClassName: "text-warn",
      Icon: ClockIcon,
    };
  }

  if (statusCode >= 200) {
    return {
      chipClassName: "border-pass-bg bg-pass-bg text-pass-ink",
      iconClassName: "text-pass",
      Icon: CheckTickIcon,
    };
  }

  return {
    chipClassName: NEUTRAL_CHIP,
    iconClassName: NEUTRAL_ICON,
    Icon: CheckTickIcon,
  };
}

export default function UrlBar({
  result,
  requestedUrl,
  onRerun,
  rerunning,
}: UrlBarProps) {
  const url = displayUrl(result.final_url ?? requestedUrl);
  const status = statusTone(result.status_code);

  const chips: {
    Icon: ComponentType<{ className?: string }>;
    label: string;
    chipClassName: string;
    iconClassName: string;
  }[] = [
    {
      Icon: ClockIcon,
      label: relativeTime(result.fetched_at),
      chipClassName: NEUTRAL_CHIP,
      iconClassName: NEUTRAL_ICON,
    },
    {
      Icon: PhoneIcon,
      label: "mobile",
      chipClassName: NEUTRAL_CHIP,
      iconClassName: NEUTRAL_ICON,
    },
    {
      Icon: status.Icon,
      label: statusLabel(result.status_code),
      chipClassName: status.chipClassName,
      iconClassName: status.iconClassName,
    },
    {
      Icon: ListIcon,
      label: `${result.checks.length} checks`,
      chipClassName: NEUTRAL_CHIP,
      iconClassName: NEUTRAL_ICON,
    },
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
          {chips.map(({ Icon, label, chipClassName, iconClassName }) => (
            <span
              key={label}
              className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${chipClassName}`}
            >
              <Icon className={`h-3.5 w-3.5 ${iconClassName}`} />
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
