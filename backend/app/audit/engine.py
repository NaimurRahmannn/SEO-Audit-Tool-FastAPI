"""Audit orchestrator: fetch a page, run every check module, assemble results.

``run_audit`` is the single entry point that ties the fetch layer, the parser,
the six check modules, and scoring together into a complete ``AuditResult``.
"""

from datetime import datetime, timezone

from app.audit.checks.headings import run_heading_checks
from app.audit.checks.images import run_image_checks
from app.audit.checks.links import run_link_checks
from app.audit.checks.meta import run_meta_checks
from app.audit.checks.social import run_social_checks
from app.audit.checks.structured_data import run_structured_data_checks
from app.audit.fetcher import FetchResult, fetch_page
from app.audit.parser import ParsedPage
from app.audit.psi import run_psi_checks
from app.models.schemas import (
    AuditResult,
    CategoryScore,
    CheckCategory,
    CheckResult,
    Severity,
)

# Fixed, intentional display order. Performance/accessibility are reserved for
# the future PageSpeed Insights integration; empty categories are not emitted.
_CATEGORY_ORDER = [
    CheckCategory.META,
    CheckCategory.HEADINGS,
    CheckCategory.IMAGES,
    CheckCategory.LINKS,
    CheckCategory.SOCIAL,
    CheckCategory.STRUCTURED_DATA,
    CheckCategory.PERFORMANCE,
    CheckCategory.ACCESSIBILITY,
]

# Severity weights used for both per-category and overall scoring.
_WEIGHTS = {
    Severity.PASS: 1.0,
    Severity.WARNING: 0.5,
    Severity.FAIL: 0.0,
}


async def run_audit(
    url: str, check_broken_links: bool = False, run_psi: bool = True
) -> AuditResult:
    """Fetch ``url``, run all checks, and return a scored ``AuditResult``."""
    fetch_result = await fetch_page(url)

    # 2. Transport/connection failure: nothing to analyze.
    if fetch_result.error is not None:
        return _result_with_error(url, fetch_result, fetch_result.error)

    # 3. Successful fetch but no HTML body (e.g. a PDF or JSON 200).
    if fetch_result.html is None:
        note = (
            "The URL did not return HTML content "
            f"(content-type: {fetch_result.content_type})."
        )
        return _result_with_error(url, fetch_result, note)

    # HTML is present: build the page and run checks (even on a 4xx/5xx body).
    page = ParsedPage.from_fetch_result(fetch_result)
    checks: list[CheckResult] = []

    # 4. HTTP error status with an HTML body: flag the status but still analyze.
    status = fetch_result.status_code
    if status is not None and status >= 400:
        checks.append(_status_check(status))

    # 5. Run every check module; links is async (and the only network-bound one).
    checks.extend(run_meta_checks(page))
    checks.extend(run_heading_checks(page))
    checks.extend(run_image_checks(page))
    checks.extend(run_social_checks(page))
    checks.extend(run_structured_data_checks(page))
    checks.extend(await run_link_checks(page, check_broken=check_broken_links))

    # PSI is best-effort: it degrades gracefully internally, but wrap it anyway
    # so an unexpected failure can never abort an otherwise-complete audit.
    if run_psi:
        try:
            checks.extend(await run_psi_checks(fetch_result.final_url or url))
        except Exception:  # noqa: BLE001 - resilience: never let PSI abort the audit
            pass

    return AuditResult(
        url=url,
        final_url=fetch_result.final_url,
        status_code=fetch_result.status_code,
        fetched_at=datetime.now(timezone.utc),
        overall_score=_overall_score(checks),
        category_scores=_score_categories(checks),
        checks=checks,
    )


def _result_with_error(url: str, fetch_result: FetchResult, message: str) -> AuditResult:
    """Build an AuditResult representing a fetch that yielded no analyzable HTML."""
    return AuditResult(
        url=url,
        final_url=fetch_result.final_url,
        status_code=fetch_result.status_code,
        fetched_at=datetime.now(timezone.utc),
        overall_score=0,
        category_scores=[],
        checks=[],
        error=message,
    )


def _status_check(status_code: int) -> CheckResult:
    """A FAIL check noting that the page returned an HTTP error status."""
    return CheckResult(
        id="fetch.status",
        title="HTTP Status",
        category=CheckCategory.META,
        severity=Severity.FAIL,
        message=f"The page returned HTTP {status_code}.",
        affected_element=str(status_code),
        recommendation="Return a 2xx status so search engines can index the page.",
    )


def _overall_score(checks: list[CheckResult]) -> int:
    """Overall score = equal-weighted average over *every* check.

    Each check counts once regardless of category, so categories with more
    checks carry proportionally more weight. This is deliberately NOT an
    average of the per-category scores.
    """
    if not checks:
        return 0
    total = sum(_WEIGHTS[c.severity] for c in checks)
    return round(total / len(checks) * 100)


def _score_categories(checks: list[CheckResult]) -> list[CategoryScore]:
    """Build a CategoryScore per non-empty category, in fixed display order."""
    scores: list[CategoryScore] = []
    for category in _CATEGORY_ORDER:
        category_checks = [c for c in checks if c.category == category]
        if not category_checks:
            continue  # Don't emit categories with nothing to evaluate.

        passed = sum(1 for c in category_checks if c.severity is Severity.PASS)
        warnings = sum(1 for c in category_checks if c.severity is Severity.WARNING)
        failed = sum(1 for c in category_checks if c.severity is Severity.FAIL)
        average = sum(_WEIGHTS[c.severity] for c in category_checks) / len(category_checks)

        scores.append(
            CategoryScore(
                category=category,
                score=round(average * 100),
                passed=passed,
                warnings=warnings,
                failed=failed,
            )
        )
    return scores
