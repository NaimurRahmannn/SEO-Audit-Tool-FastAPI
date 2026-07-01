import { FlagIcon } from "@/components/icons";
import { categoryLabel, priorityFixes } from "@/lib/audit-format";
import { SEV_BADGE, SEV_RANK } from "@/lib/audit-styles";
import type { AuditResult } from "@/lib/types";

export default function PriorityFixes({ result }: { result: AuditResult }) {
  const fixes = priorityFixes(result.checks);
  if (fixes.length === 0) return null; // perfect score -> hide entirely

  return (
    <div className="rounded-2xl border border-line bg-surface p-6">
      <h3 className="flex items-center gap-2 text-base font-bold text-ink">
        <FlagIcon className="h-4 w-4 text-fail" />
        Top priority fixes
      </h3>

      <ol className="mt-4 divide-y divide-line">
        {fixes.map((check, index) => (
          <li
            key={check.id}
            className="flex items-center gap-4 py-4 first:pt-0 last:pb-0"
          >
            <span
              className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${SEV_RANK[check.severity]}`}
            >
              {index + 1}
            </span>
            <div className="min-w-0 flex-1">
              <p className="font-semibold text-ink">{check.title}</p>
              <p className="mt-0.5 truncate text-sm text-ink-3">
                {categoryLabel(check.category)} · {check.message}
              </p>
            </div>
            <span
              className={`shrink-0 rounded-md px-2 py-1 text-xs font-bold uppercase tracking-wide ${SEV_BADGE[check.severity]}`}
            >
              {check.severity === "fail" ? "Critical" : "Warning"}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
