"""Tests for app.audit.checks.headings.run_heading_checks."""

from app.audit.checks.headings import run_heading_checks
from app.audit.parser import ParsedPage
from app.models.schemas import CheckCategory, Severity

BASE_URL = "https://example.com/"


def _page(body: str) -> ParsedPage:
    html = f"<!DOCTYPE html><html><head></head><body>{body}</body></html>"
    return ParsedPage(html, BASE_URL)


def _result(page: ParsedPage, check_id: str):
    return next(r for r in run_heading_checks(page) if r.id == check_id)


def test_all_results_are_headings_category():
    page = _page("<h1>Title</h1><h2>Sub</h2>")
    assert all(r.category is CheckCategory.HEADINGS for r in run_heading_checks(page))


# ---- H1 presence ----------------------------------------------------------


def test_h1_pass_single():
    r = _result(_page("<h1>Main</h1><h2>Sub</h2>"), "headings.h1.presence")
    assert r.severity is Severity.PASS
    assert r.recommendation is None


def test_h1_fail_none():
    r = _result(_page("<h2>Sub only</h2>"), "headings.h1.presence")
    assert r.severity is Severity.FAIL
    assert r.affected_element == "no <h1> found"


def test_h1_warning_multiple():
    r = _result(_page("<h1>First</h1><h1>Second</h1>"), "headings.h1.presence")
    assert r.severity is Severity.WARNING
    assert "2" in r.message
    assert r.affected_element == "First | Second"


# ---- Hierarchy ------------------------------------------------------------


def test_hierarchy_pass_clean():
    body = "<h1>A</h1><h2>B</h2><h3>C</h3><h2>D</h2>"
    r = _result(_page(body), "headings.hierarchy")
    assert r.severity is Severity.PASS
    assert r.affected_element == "h1 > h2 > h3 > h2"


def test_hierarchy_warning_skipped_level():
    body = "<h1>A</h1><h2>B</h2><h4>D</h4>"  # skips h3
    r = _result(_page(body), "headings.hierarchy")
    assert r.severity is Severity.WARNING
    assert "<h4>" in r.message and "<h2>" in r.message and "<h3>" in r.message


# ---- Empty headings -------------------------------------------------------


def test_empty_pass():
    r = _result(_page("<h1>Has text</h1>"), "headings.empty")
    assert r.severity is Severity.PASS
    assert r.affected_element is None


def test_empty_warning():
    body = "<h1>Main</h1><h2>   </h2><h3></h3>"
    r = _result(_page(body), "headings.empty")
    assert r.severity is Severity.WARNING
    assert "2" in r.message
    assert r.affected_element == "<h2>, <h3>"


# ---- No headings at all ---------------------------------------------------


def test_no_headings_emits_presence_only():
    results = run_heading_checks(_page("<p>No headings here.</p>"))
    ids = {r.id for r in results}
    assert ids == {"headings.presence"}
    assert results[0].severity is Severity.FAIL


def test_headings_present_omits_presence_check():
    results = run_heading_checks(_page("<h1>Has a heading</h1>"))
    ids = {r.id for r in results}
    assert "headings.presence" not in ids
    assert ids == {"headings.h1.presence", "headings.hierarchy", "headings.empty"}
