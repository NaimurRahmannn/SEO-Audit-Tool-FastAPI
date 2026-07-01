import { countBySeverity, verdictForScore } from "@/lib/audit-format";
import type { AuditResult } from "@/lib/types";
import ScoreRing from "./ScoreRing";
import SeverityTiers from "./SeverityTiers";

export default function ScoreHero({ result }: { result: AuditResult }) {
  const counts = countBySeverity(result.checks);
  const verdict = verdictForScore(result.overall_score, counts.fail);

  return (
    <div className="rounded-2xl border border-line bg-surface p-6 sm:p-8">
      <div className="grid gap-8 md:grid-cols-[1.4fr_1fr] md:divide-x md:divide-line">
        <div className="flex flex-col items-center gap-6 sm:flex-row md:pr-8">
          <ScoreRing score={result.overall_score} />
          <div className="text-center sm:text-left">
            <h2 className="text-2xl font-extrabold tracking-tight text-ink">
              {verdict.title}
            </h2>
            <p className="mt-2 leading-relaxed text-ink-2">{verdict.summary}</p>
          </div>
        </div>

        <div className="md:pl-8">
          <SeverityTiers counts={counts} />
        </div>
      </div>
    </div>
  );
}
