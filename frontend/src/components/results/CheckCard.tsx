import {
  CheckTickIcon,
  LightbulbIcon,
  TriangleAlertIcon,
  XIcon,
} from "@/components/icons";
import { SEVERITY_LABELS } from "@/lib/audit-format";
import { SEV_BADGE, SEV_BAR, SEV_RECO } from "@/lib/audit-styles";
import type { CheckResult, Severity } from "@/lib/types";

const SEV_ICON: Record<Severity, typeof CheckTickIcon> = {
  pass: CheckTickIcon,
  warning: TriangleAlertIcon,
  fail: XIcon,
};

export default function CheckCard({ check }: { check: CheckResult }) {
  const { severity } = check;
  const SevIcon = SEV_ICON[severity];
  const affectedElement = check.affected_element?.trim();
  const recommendation = check.recommendation?.trim();

  return (
    <div className="relative overflow-hidden rounded-xl border border-line bg-surface">
      <span
        className={`absolute inset-y-0 left-0 w-1.5 ${SEV_BAR[severity]}`}
        aria-hidden="true"
      />
      <div className="p-5 pl-6">
        <div className="flex flex-wrap items-center gap-3">
          <span
            className={`inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-bold uppercase tracking-wide ${SEV_BADGE[severity]}`}
          >
            <SevIcon className="h-3.5 w-3.5" />
            {SEVERITY_LABELS[severity]}
          </span>
          <h4 className="min-w-0 break-words font-bold text-ink [overflow-wrap:anywhere]">
            {check.title}
          </h4>
        </div>

        <p className="mt-2 break-words text-ink-2 [overflow-wrap:anywhere]">
          {check.message}
        </p>

        {affectedElement && (
          <div className="mt-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-ink-3">
              Where
            </p>
            <p className="mt-1.5 whitespace-pre-wrap break-all rounded-lg bg-soft px-3 py-2 font-mono text-sm text-ink-2 [overflow-wrap:anywhere]">
              {affectedElement}
            </p>
          </div>
        )}

        {recommendation && (
          <div
            className={`mt-4 flex items-start gap-2 rounded-lg px-3 py-2.5 text-sm ${SEV_RECO[severity]}`}
          >
            <LightbulbIcon className="mt-0.5 h-4 w-4 shrink-0" />
            <span className="min-w-0 break-words [overflow-wrap:anywhere]">
              {recommendation}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
