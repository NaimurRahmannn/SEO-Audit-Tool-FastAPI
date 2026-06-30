"""Tests for app.audit.engine.run_audit and its scoring helpers."""

import pytest

from app.audit import engine
from app.audit.engine import _overall_score, _score_categories, run_audit
from app.audit.fetcher import FetchResult
from app.models.schemas import CheckCategory, CheckResult, Severity

CLEAN_HTML = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>A Reasonably Descriptive Page Title Here</title>
    <meta name="description"
          content="A meta description that is comfortably within the recommended fifty to one hundred sixty character window.">
    <link rel="canonical" href="https://example.com/">
    <meta property="og:title" content="T">
    <meta property="og:description" content="D">
    <meta property="og:image" content="https://example.com/i.png">
    <meta property="og:url" content="https://example.com/">
    <meta property="og:type" content="website">
    <script type="application/ld+json">{"@type": "WebSite"}</script>
  </head>
  <body>
    <h1>Main Heading</h1>
    <h2>Section</h2>
    <a href="/about">About</a>
    <img src="/a.png" alt="A picture">
  </body>
</html>
"""


def _patch_fetch(monkeypatch, fetch_result: FetchResult):
    async def _fake_fetch(url: str) -> FetchResult:
        return fetch_result

    monkeypatch.setattr(engine, "fetch_page", _fake_fetch)


def _check(category: CheckCategory, severity: Severity, cid: str = "x") -> CheckResult:
    return CheckResult(
        id=cid, title=cid, category=category, severity=severity, message="m"
    )


# ---- Clean page -----------------------------------------------------------


@pytest.mark.asyncio
async def test_clean_page_runs_checks_and_scores(monkeypatch):
    _patch_fetch(
        monkeypatch,
        FetchResult(
            requested_url="https://example.com/",
            final_url="https://example.com/",
            status_code=200,
            html=CLEAN_HTML,
            content_type="text/html",
        ),
    )

    result = await run_audit("https://example.com/")

    assert result.error is None
    assert len(result.checks) > 0
    assert len(result.category_scores) > 0
    assert 0 <= result.overall_score <= 100
    # No fetch.status check on a 200.
    assert all(c.id != "fetch.status" for c in result.checks)
    # Overall is the equal-weight average over every check.
    weights = {Severity.PASS: 1.0, Severity.WARNING: 0.5, Severity.FAIL: 0.0}
    expected = round(sum(weights[c.severity] for c in result.checks) / len(result.checks) * 100)
    assert result.overall_score == expected


@pytest.mark.asyncio
async def test_category_scores_in_fixed_order(monkeypatch):
    _patch_fetch(
        monkeypatch,
        FetchResult(
            requested_url="https://example.com/",
            final_url="https://example.com/",
            status_code=200,
            html=CLEAN_HTML,
            content_type="text/html",
        ),
    )
    result = await run_audit("https://example.com/", run_psi=False)
    order = [cs.category for cs in result.category_scores]
    expected_order = [
        CheckCategory.META,
        CheckCategory.HEADINGS,
        CheckCategory.IMAGES,
        CheckCategory.LINKS,
        CheckCategory.SOCIAL,
        CheckCategory.STRUCTURED_DATA,
    ]
    assert order == expected_order
    # Performance/accessibility have no checks yet -> omitted.
    assert CheckCategory.PERFORMANCE not in order
    assert CheckCategory.ACCESSIBILITY not in order


# ---- Fetch error ----------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_error_returns_zero_score_no_checks(monkeypatch):
    _patch_fetch(
        monkeypatch,
        FetchResult(
            requested_url="https://nope.invalid/",
            final_url="https://nope.invalid/",
            status_code=None,
            html=None,
            error="Could not connect to the host",
        ),
    )

    result = await run_audit("https://nope.invalid/")

    assert result.error == "Could not connect to the host"
    assert result.overall_score == 0
    assert result.checks == []
    assert result.category_scores == []


# ---- Non-HTML response ----------------------------------------------------


@pytest.mark.asyncio
async def test_non_html_response_sets_error_note(monkeypatch):
    _patch_fetch(
        monkeypatch,
        FetchResult(
            requested_url="https://example.com/file.pdf",
            final_url="https://example.com/file.pdf",
            status_code=200,
            html=None,
            content_type="application/pdf",
        ),
    )

    result = await run_audit("https://example.com/file.pdf")

    assert result.error is not None
    assert "application/pdf" in result.error
    assert result.overall_score == 0
    assert result.checks == []


# ---- HTTP 404 with HTML ---------------------------------------------------


@pytest.mark.asyncio
async def test_http_404_with_html_flags_status_and_runs_checks(monkeypatch):
    _patch_fetch(
        monkeypatch,
        FetchResult(
            requested_url="https://example.com/missing",
            final_url="https://example.com/missing",
            status_code=404,
            html=CLEAN_HTML,
            content_type="text/html",
        ),
    )

    result = await run_audit("https://example.com/missing")

    status_checks = [c for c in result.checks if c.id == "fetch.status"]
    assert len(status_checks) == 1
    assert status_checks[0].severity is Severity.FAIL
    assert "404" in status_checks[0].message
    # Checks still ran on the body.
    assert any(c.id == "meta.title" for c in result.checks)
    assert result.status_code == 404


# ---- Scoring weights checks equally, not categories -----------------------


def test_overall_weights_checks_equally_not_categories():
    # 1 META pass (cat score 100) + 3 LINKS fails (cat score 0).
    checks = [
        _check(CheckCategory.META, Severity.PASS, "m1"),
        _check(CheckCategory.LINKS, Severity.FAIL, "l1"),
        _check(CheckCategory.LINKS, Severity.FAIL, "l2"),
        _check(CheckCategory.LINKS, Severity.FAIL, "l3"),
    ]

    overall = _overall_score(checks)
    # Equal weighting over checks: (1.0 + 0 + 0 + 0) / 4 * 100 = 25.
    assert overall == 25

    cats = _score_categories(checks)
    naive_category_average = round(sum(c.score for c in cats) / len(cats))
    # Naive average of category scores would be (100 + 0) / 2 = 50.
    assert naive_category_average == 50
    assert overall != naive_category_average


def test_overall_score_empty_is_zero():
    assert _overall_score([]) == 0
