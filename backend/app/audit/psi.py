"""PageSpeed Insights (PSI) integration.

Adds real Lighthouse-based performance, SEO, and accessibility signals to the
audit. The whole integration degrades gracefully: a missing API key, a slow or
failing PSI call, or an unexpected response shape all yield a single WARNING
``CheckResult`` rather than raising — a PSI problem must never abort an audit.
"""

import httpx

from app.config import settings
from app.models.schemas import CheckCategory, CheckResult, Severity

PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# PSI is slow; give it a generous budget.
_TIMEOUT = httpx.Timeout(30.0)

# Lighthouse category key -> (check id, our category, human label).
# The SEO score lives under PERFORMANCE so it renders alongside the performance
# signals rather than in its own near-empty section.
_LH_CATEGORIES = {
    "performance": ("performance.lighthouse", CheckCategory.PERFORMANCE, "performance"),
    "seo": ("performance.seo.lighthouse", CheckCategory.PERFORMANCE, "SEO"),
    "accessibility": ("accessibility.lighthouse", CheckCategory.ACCESSIBILITY, "accessibility"),
}

# Core Web Vitals audits to surface (Lighthouse audit id -> short label).
_WEB_VITALS = [
    ("largest-contentful-paint", "LCP"),
    ("cumulative-layout-shift", "CLS"),
    ("total-blocking-time", "TBT"),
]


async def run_psi_checks(url: str) -> list[CheckResult]:
    """Run PageSpeed Insights against ``url`` and map results to CheckResults."""
    api_key = settings.PSI_API_KEY
    if not api_key:
        return [_unavailable_result()]

    params = [
        ("url", url),
        ("key", api_key),
        ("strategy", "mobile"),
        ("category", "PERFORMANCE"),
        ("category", "SEO"),
        ("category", "ACCESSIBILITY"),
    ]

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.get(PSI_ENDPOINT, params=params)
    except (httpx.TimeoutException, httpx.RequestError):
        return [_error_result("network error or timeout")]

    if response.status_code != 200:
        return [_error_result(f"HTTP {response.status_code}")]

    try:
        lighthouse = response.json()["lighthouseResult"]
        categories = lighthouse["categories"]
    except (ValueError, KeyError, TypeError):
        return [_error_result("unexpected response shape")]

    results: list[CheckResult] = []
    for key, (check_id, category, label) in _LH_CATEGORIES.items():
        node = categories.get(key)
        if isinstance(node, dict):
            results.append(_category_result(check_id, category, label, node.get("score")))

    vitals = _web_vitals_result(lighthouse.get("audits"))
    if vitals is not None:
        results.append(vitals)

    # If nothing recognizable came back, treat it as an error rather than a
    # silent empty list.
    if not results:
        return [_error_result("no Lighthouse categories returned")]

    return results


def _category_result(
    check_id: str, category: CheckCategory, label: str, raw_score: float | None
) -> CheckResult:
    title = f"Lighthouse {label.capitalize()}"

    if raw_score is None:
        return CheckResult(
            id=check_id,
            title=title,
            category=category,
            severity=Severity.WARNING,
            message=f"Lighthouse {label} score is unavailable.",
            affected_element=None,
            recommendation=f"Re-run PageSpeed Insights; the {label} score could not be computed.",
        )

    score = round(raw_score * 100)
    severity = _severity_for(score)
    recommendation = None
    if severity is not Severity.PASS:
        recommendation = _recommendation_for(label)

    return CheckResult(
        id=check_id,
        title=title,
        category=category,
        severity=severity,
        message=f"Lighthouse {label} score: {score}/100.",
        affected_element=str(score),
        recommendation=recommendation,
    )


def _severity_for(score: int) -> Severity:
    """Lighthouse's own banding: >=90 good, 50-89 needs work, <50 poor."""
    if score >= 90:
        return Severity.PASS
    if score >= 50:
        return Severity.WARNING
    return Severity.FAIL


def _recommendation_for(label: str) -> str:
    if label == "SEO":
        return (
            "Review the Lighthouse SEO audits; this score reflects crawlability, "
            "meta tags, and mobile-friendliness."
        )
    return f"Review the Lighthouse {label} audits and address the flagged opportunities."


def _web_vitals_result(audits: object) -> CheckResult | None:
    """Build an informational Core Web Vitals result, or None if unavailable."""
    if not isinstance(audits, dict):
        return None

    parts: list[str] = []
    for audit_id, short in _WEB_VITALS:
        node = audits.get(audit_id)
        if isinstance(node, dict) and node.get("displayValue"):
            parts.append(f"{short} {node['displayValue']}")

    if not parts:
        return None

    return CheckResult(
        id="performance.web_vitals",
        title="Core Web Vitals",
        category=CheckCategory.PERFORMANCE,
        severity=Severity.PASS,
        message="Core Web Vitals — " + ", ".join(parts) + ".",
        affected_element=None,
        recommendation=None,
    )


def _unavailable_result() -> CheckResult:
    return CheckResult(
        id="performance.psi.unavailable",
        title="PageSpeed Insights",
        category=CheckCategory.PERFORMANCE,
        severity=Severity.WARNING,
        message=(
            "PageSpeed Insights is not configured (no API key); performance, SEO, "
            "and accessibility scores were skipped."
        ),
        affected_element=None,
        recommendation="Set PSI_API_KEY to enable Lighthouse-based scoring.",
    )


def _error_result(detail: str = "") -> CheckResult:
    message = (
        "Could not reach PageSpeed Insights; performance and accessibility "
        "scores were skipped."
    )
    if detail:
        message += f" ({detail})"
    return CheckResult(
        id="performance.psi.error",
        title="PageSpeed Insights",
        category=CheckCategory.PERFORMANCE,
        severity=Severity.WARNING,
        message=message,
        affected_element=None,
        recommendation="Verify the API key and that PageSpeed Insights is reachable.",
    )
