import type { SeverityCounts } from "@/lib/audit-format";

type TierKey = keyof SeverityCounts;

const TIERS: { key: TierKey; label: string; box: string; dot: string; ink: string }[] = [
  { key: "fail", label: "Critical issues", box: "bg-fail-bg", dot: "bg-fail", ink: "text-fail-ink" },
  { key: "warning", label: "Warnings", box: "bg-warn-bg", dot: "bg-warn", ink: "text-warn-ink" },
  { key: "pass", label: "Passed checks", box: "bg-pass-bg", dot: "bg-pass", ink: "text-pass-ink" },
];

export default function SeverityTiers({ counts }: { counts: SeverityCounts }) {
  return (
    <div className="flex flex-col gap-3">
      {TIERS.map((tier) => (
        <div
          key={tier.key}
          className={`flex items-center gap-3 rounded-xl ${tier.box} px-4 py-3`}
        >
          <span className={`h-2.5 w-2.5 shrink-0 rounded-sm ${tier.dot}`} aria-hidden="true" />
          <span className="text-xl font-extrabold text-ink">{counts[tier.key]}</span>
          <span className={`text-sm font-semibold ${tier.ink}`}>{tier.label}</span>
        </div>
      ))}
    </div>
  );
}
