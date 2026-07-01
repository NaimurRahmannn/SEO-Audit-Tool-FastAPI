import { bandForScore, categoryLabel, countsLabel } from "@/lib/audit-format";
import { BAND_BAR, BAND_TEXT } from "@/lib/audit-styles";
import type { CategoryScore } from "@/lib/types";
import { categoryIcon } from "./category-icons";

export default function CategoryStrip({ scores }: { scores: CategoryScore[] }) {
  return (
    <div className="divide-y divide-line rounded-2xl border border-line bg-surface px-5 sm:px-6">
      {scores.map((score) => {
        const band = bandForScore(score.score);
        const Icon = categoryIcon(score.category);
        return (
          <div key={score.category} className="flex items-center gap-3 py-4 sm:gap-4">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-soft text-ink-2">
              <Icon className="h-5 w-5" />
            </span>
            <span className="w-20 shrink-0 truncate font-semibold text-ink sm:w-32">
              {categoryLabel(score.category)}
            </span>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-line">
              <div
                className={`h-full rounded-full ${BAND_BAR[band]}`}
                style={{ width: `${score.score}%` }}
              />
            </div>
            <span className={`w-10 shrink-0 text-right font-bold ${BAND_TEXT[band]}`}>
              {score.score}
            </span>
            <span className="hidden w-32 shrink-0 text-right text-xs text-ink-3 sm:block">
              {countsLabel(score.passed, score.warnings, score.failed)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
