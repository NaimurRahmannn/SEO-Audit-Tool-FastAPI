import type { AuditResult } from "@/lib/types";
import CategoryStrip from "./CategoryStrip";
import CheckSection from "./CheckSection";
import PriorityFixes from "./PriorityFixes";
import ScoreHero from "./ScoreHero";
import UrlBar from "./UrlBar";

interface AuditReportProps {
  result: AuditResult;
  requestedUrl: string;
  onRerun: () => void;
  rerunning: boolean;
}

export default function AuditReport({
  result,
  requestedUrl,
  onRerun,
  rerunning,
}: AuditReportProps) {
  return (
    <div className="space-y-8">
      <UrlBar
        result={result}
        requestedUrl={requestedUrl}
        onRerun={onRerun}
        rerunning={rerunning}
      />

      <ScoreHero result={result} />

      <PriorityFixes result={result} />

      <div>
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-ink-3">
          Category breakdown
        </h2>
        <CategoryStrip scores={result.category_scores} />
      </div>

      <div>
        {result.category_scores.map((score) => (
          <CheckSection
            key={score.category}
            category={score.category}
            checks={result.checks.filter((c) => c.category === score.category)}
          />
        ))}
      </div>
    </div>
  );
}
