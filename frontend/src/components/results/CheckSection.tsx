import { categoryLabel } from "@/lib/audit-format";
import type { CheckCategory, CheckResult } from "@/lib/types";
import CheckCard from "./CheckCard";

interface CheckSectionProps {
  category: CheckCategory;
  checks: CheckResult[];
}

export default function CheckSection({ category, checks }: CheckSectionProps) {
  if (checks.length === 0) return null;

  return (
    <section className="mt-10">
      <div className="flex items-center gap-3 border-b border-line pb-3">
        <h3 className="text-lg font-bold tracking-tight text-ink">
          {categoryLabel(category)}
        </h3>
        <span className="rounded-full bg-soft px-2.5 py-0.5 text-xs font-semibold text-ink-3">
          {checks.length} {checks.length === 1 ? "check" : "checks"}
        </span>
      </div>

      <div className="mt-4 space-y-4">
        {checks.map((check) => (
          <CheckCard key={check.id} check={check} />
        ))}
      </div>
    </section>
  );
}
