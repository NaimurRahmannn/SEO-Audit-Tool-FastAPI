// Thin typed client for the audit backend.

import type { AuditJobResponse } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/** Parse a response, throwing a useful Error on any non-2xx status. */
async function parse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (body?.detail) {
        detail =
          typeof body.detail === "string"
            ? body.detail
            : JSON.stringify(body.detail);
      }
    } catch {
      // Response had no JSON body; fall back to statusText.
    }
    throw new Error(`Request failed (${response.status}): ${detail}`);
  }
  return response.json() as Promise<T>;
}

/** Start a new audit job. POST /api/audit */
export async function startAudit(
  url: string,
  checkBrokenLinks: boolean
): Promise<AuditJobResponse> {
  const response = await fetch(`${API_BASE_URL}/api/audit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, check_broken_links: checkBrokenLinks }),
  });
  return parse<AuditJobResponse>(response);
}

/** Fetch the current state of an audit job. GET /api/audit/{jobId} */
export async function getAudit(jobId: string): Promise<AuditJobResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/audit/${encodeURIComponent(jobId)}`,
    { method: "GET" }
  );
  return parse<AuditJobResponse>(response);
}
