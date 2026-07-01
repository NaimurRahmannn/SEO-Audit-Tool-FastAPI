// Pure presentation helpers for audit data. No React, no styling — just
// human-readable labels and derived values from the AuditResult data shapes.

import type { CheckCategory, CheckResult, Severity } from "./types";

export const CATEGORY_LABELS: Record<CheckCategory, string> = {
  meta: "Meta",
  headings: "Headings",
  images: "Images",
  links: "Links",
  social: "Social",
  structured_data: "Structured Data",
  performance: "Performance",
  accessibility: "Accessibility",
};

export function categoryLabel(category: CheckCategory): string {
  return CATEGORY_LABELS[category] ?? category;
}

export const SEVERITY_LABELS: Record<Severity, string> = {
  pass: "Pass",
  warning: "Warning",
  fail: "Fail",
};

/** Letter grade banding: A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 50, F < 50. */
export function gradeForScore(score: number): string {
  if (score >= 90) return "A";
  if (score >= 80) return "B";
  if (score >= 70) return "C";
  if (score >= 50) return "D";
  return "F";
}

export type Band = "green" | "amber" | "red";

/** Color band: green ≥ 80, amber 50–79, red < 50. */
export function bandForScore(score: number): Band {
  if (score >= 80) return "green";
  if (score >= 50) return "amber";
  return "red";
}

export interface SeverityCounts {
  pass: number;
  warning: number;
  fail: number;
}

export function countBySeverity(checks: CheckResult[]): SeverityCounts {
  const counts: SeverityCounts = { pass: 0, warning: 0, fail: 0 };
  for (const check of checks) {
    counts[check.severity] += 1;
  }
  return counts;
}

/** Top issues: all fails first, then all warnings, capped at 3. */
export function priorityFixes(checks: CheckResult[]): CheckResult[] {
  const fails = checks.filter((c) => c.severity === "fail");
  const warnings = checks.filter((c) => c.severity === "warning");
  return [...fails, ...warnings].slice(0, 3);
}

export function verdictForScore(
  score: number,
  failCount: number
): { title: string; summary: string } {
  const issues = failCount === 1 ? "1 critical issue" : `${failCount} critical issues`;

  if (score >= 90) {
    return {
      title: "Excellent",
      summary: failCount
        ? `Nearly there — resolve the ${issues} below to lock in a top score.`
        : "A polished page with no critical issues found.",
    };
  }
  if (score >= 80) {
    return {
      title: "Strong",
      summary: failCount
        ? `A strong SEO foundation. Resolve the ${issues} below to reach an A grade.`
        : "A strong SEO foundation with no critical issues.",
    };
  }
  if (score >= 50) {
    return {
      title: "Good, needs work",
      summary: failCount
        ? `A solid start. Resolve the ${issues} below to move up a grade.`
        : "A solid start with room to improve.",
    };
  }
  return {
    title: "Needs attention",
    summary: failCount
      ? `Several problems to fix. Start with the ${issues} below.`
      : "Several problems to fix — review the checks below.",
  };
}

/** Strip the scheme and trailing slash for a compact display URL. */
export function displayUrl(url: string): string {
  return url.replace(/^https?:\/\//, "").replace(/\/$/, "");
}

const STATUS_TEXT: Record<number, string> = {
  200: "OK",
  201: "Created",
  204: "No Content",
  301: "Moved",
  302: "Found",
  304: "Not Modified",
  307: "Redirect",
  308: "Redirect",
  400: "Bad Request",
  401: "Unauthorized",
  403: "Forbidden",
  404: "Not Found",
  410: "Gone",
  429: "Too Many",
  500: "Server Error",
  502: "Bad Gateway",
  503: "Unavailable",
};

export function statusLabel(code: number | null): string {
  if (code == null) return "No status";
  const text = STATUS_TEXT[code];
  return text ? `${code} ${text}` : String(code);
}

export function relativeTime(iso: string): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "just now";
  const seconds = Math.max(0, Math.floor((Date.now() - then) / 1000));
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

/** Compact "3 pass · 1 warn" style summary, omitting zero counts. */
export function countsLabel(passed: number, warnings: number, failed: number): string {
  const parts: string[] = [];
  if (passed) parts.push(`${passed} pass`);
  if (warnings) parts.push(`${warnings} warn`);
  if (failed) parts.push(`${failed} fail`);
  return parts.join(" · ") || "no checks";
}
