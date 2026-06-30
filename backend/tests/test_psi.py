"""Tests for app.audit.psi.run_psi_checks and engine PSI wiring."""

import httpx
import pytest
import respx

from app.audit import engine, psi
from app.audit.engine import run_audit
from app.audit.fetcher import FetchResult
from app.audit.psi import PSI_ENDPOINT, run_psi_checks
from app.models.schemas import CheckCategory, CheckResult, Severity


def _psi_json(perf=0.82, seo=0.95, a11y=0.40, with_audits=True):
    body = {
        "lighthouseResult": {
            "categories": {
                "performance": {"score": perf},
                "seo": {"score": seo},
                "accessibility": {"score": a11y},
            }
        }
    }
    if with_audits:
        body["lighthouseResult"]["audits"] = {
            "largest-contentful-paint": {"displayValue": "2.1 s"},
            "cumulative-layout-shift": {"displayValue": "0.05"},
            "total-blocking-time": {"displayValue": "120 ms"},
        }
    return body


def _by_id(results, check_id):
    return next((r for r in results if r.id == check_id), None)


# ---- No API key -----------------------------------------------------------


@pytest.mark.asyncio
async def test_no_api_key_returns_unavailable(monkeypatch):
    monkeypatch.setattr(psi.settings, "PSI_API_KEY", "")
    results = await run_psi_checks("https://example.com/")
    assert len(results) == 1
    assert results[0].id == "performance.psi.unavailable"
    assert results[0].severity is Severity.WARNING
    assert results[0].category is CheckCategory.PERFORMANCE


# ---- Successful response --------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_successful_psi_maps_categories(monkeypatch):
    monkeypatch.setattr(psi.settings, "PSI_API_KEY", "k")
    respx.get(url__startswith=PSI_ENDPOINT).mock(
        return_value=httpx.Response(200, json=_psi_json())
    )

    results = await run_psi_checks("https://example.com/")

    perf = _by_id(results, "performance.lighthouse")
    seo = _by_id(results, "performance.seo.lighthouse")
    a11y = _by_id(results, "accessibility.lighthouse")
    vitals = _by_id(results, "performance.web_vitals")

    # 82 -> WARNING (50-89), 95 -> PASS (>=90), 40 -> FAIL (<50)
    assert perf.severity is Severity.WARNING
    assert perf.message == "Lighthouse performance score: 82/100."
    assert perf.affected_element == "82"
    assert seo.severity is Severity.PASS
    assert a11y.severity is Severity.FAIL
    assert a11y.category is CheckCategory.ACCESSIBILITY

    # Web vitals present and informational.
    assert vitals is not None
    assert vitals.severity is Severity.PASS
    assert "LCP 2.1 s" in vitals.message
    assert "CLS 0.05" in vitals.message
    assert "TBT 120 ms" in vitals.message


@pytest.mark.asyncio
@respx.mock
async def test_no_audits_skips_web_vitals(monkeypatch):
    monkeypatch.setattr(psi.settings, "PSI_API_KEY", "k")
    respx.get(url__startswith=PSI_ENDPOINT).mock(
        return_value=httpx.Response(200, json=_psi_json(with_audits=False))
    )
    results = await run_psi_checks("https://example.com/")
    assert _by_id(results, "performance.web_vitals") is None


# ---- Null score -----------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_null_score_is_warning_unavailable(monkeypatch):
    monkeypatch.setattr(psi.settings, "PSI_API_KEY", "k")
    respx.get(url__startswith=PSI_ENDPOINT).mock(
        return_value=httpx.Response(200, json=_psi_json(perf=None))
    )
    results = await run_psi_checks("https://example.com/")
    perf = _by_id(results, "performance.lighthouse")
    assert perf.severity is Severity.WARNING
    assert "unavailable" in perf.message


# ---- Errors ---------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_http_error_returns_error_warning(monkeypatch):
    monkeypatch.setattr(psi.settings, "PSI_API_KEY", "k")
    respx.get(url__startswith=PSI_ENDPOINT).mock(return_value=httpx.Response(500))
    results = await run_psi_checks("https://example.com/")
    assert len(results) == 1
    assert results[0].id == "performance.psi.error"
    assert results[0].severity is Severity.WARNING


@pytest.mark.asyncio
@respx.mock
async def test_timeout_returns_error_warning(monkeypatch):
    monkeypatch.setattr(psi.settings, "PSI_API_KEY", "k")
    respx.get(url__startswith=PSI_ENDPOINT).mock(side_effect=httpx.ConnectTimeout("slow"))
    results = await run_psi_checks("https://example.com/")
    assert len(results) == 1
    assert results[0].id == "performance.psi.error"


@pytest.mark.asyncio
@respx.mock
async def test_unexpected_shape_returns_error_warning(monkeypatch):
    monkeypatch.setattr(psi.settings, "PSI_API_KEY", "k")
    respx.get(url__startswith=PSI_ENDPOINT).mock(
        return_value=httpx.Response(200, json={"unexpected": True})
    )
    results = await run_psi_checks("https://example.com/")
    assert results[0].id == "performance.psi.error"


# ---- Engine wiring --------------------------------------------------------

_HTML = """
<html><head><title>Some Page Title That Is About Forty Chars</title>
<meta name="description" content="A description long enough to fall within the recommended range of fifty to one hundred sixty.">
</head><body><h1>Hi</h1><a href="/x">x</a></body></html>
"""


def _patch_fetch(monkeypatch):
    async def _fake_fetch(url: str) -> FetchResult:
        return FetchResult(
            requested_url=url,
            final_url=url,
            status_code=200,
            html=_HTML,
            content_type="text/html",
        )

    monkeypatch.setattr(engine, "fetch_page", _fake_fetch)


def _fake_psi_results():
    async def _fake(url: str):
        return [
            CheckResult(
                id="performance.lighthouse",
                title="Lighthouse Performance",
                category=CheckCategory.PERFORMANCE,
                severity=Severity.PASS,
                message="ok",
            ),
            CheckResult(
                id="accessibility.lighthouse",
                title="Lighthouse Accessibility",
                category=CheckCategory.ACCESSIBILITY,
                severity=Severity.WARNING,
                message="ok",
            ),
        ]

    return _fake


@pytest.mark.asyncio
async def test_engine_with_psi_populates_perf_and_a11y(monkeypatch):
    _patch_fetch(monkeypatch)
    monkeypatch.setattr(engine, "run_psi_checks", _fake_psi_results())

    result = await run_audit("https://example.com/", run_psi=True)

    cats = {cs.category for cs in result.category_scores}
    assert CheckCategory.PERFORMANCE in cats
    assert CheckCategory.ACCESSIBILITY in cats
    # Fixed order keeps performance before accessibility, both after the rest.
    order = [cs.category for cs in result.category_scores]
    assert order.index(CheckCategory.PERFORMANCE) < order.index(CheckCategory.ACCESSIBILITY)


@pytest.mark.asyncio
async def test_engine_without_psi_omits_perf_and_a11y(monkeypatch):
    _patch_fetch(monkeypatch)
    result = await run_audit("https://example.com/", run_psi=False)
    cats = {cs.category for cs in result.category_scores}
    assert CheckCategory.PERFORMANCE not in cats
    assert CheckCategory.ACCESSIBILITY not in cats
