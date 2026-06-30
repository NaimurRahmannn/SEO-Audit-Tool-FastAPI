// TypeScript mirror of the backend Pydantic schemas (app/models/schemas.py and
// api_schemas.py). Keep these aligned with the backend's JSON shape.

export type Severity = "pass" | "warning" | "fail";

export type CheckCategory =
  | "meta"
  | "headings"
  | "images"
  | "links"
  | "social"
  | "structured_data"
  | "performance"
  | "accessibility";

export type JobStatus = "pending" | "running" | "done" | "failed";

export interface CheckResult {
  id: string;
  title: string;
  category: CheckCategory;
  severity: Severity;
  message: string;
  affected_element: string | null;
  recommendation: string | null;
}

export interface CategoryScore {
  category: CheckCategory;
  score: number;
  passed: number;
  warnings: number;
  failed: number;
}

export interface AuditResult {
  url: string;
  final_url: string | null;
  status_code: number | null;
  fetched_at: string; // ISO 8601 datetime
  overall_score: number;
  category_scores: CategoryScore[];
  checks: CheckResult[];
  error: string | null;
}

export interface AuditJobResponse {
  id: string;
  url: string;
  status: JobStatus;
  created_at: string; // ISO 8601 datetime
  result: AuditResult | null;
  error: string | null;
}
