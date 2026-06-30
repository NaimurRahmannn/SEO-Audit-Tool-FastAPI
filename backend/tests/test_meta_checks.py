"""Tests for app.audit.checks.meta.run_meta_checks."""

from app.audit.checks.meta import run_meta_checks
from app.audit.parser import ParsedPage
from app.models.schemas import CheckCategory, Severity

BASE_URL = "https://example.com/"


def _page(head: str = "", body: str = "") -> ParsedPage:
    html = f"<!DOCTYPE html><html><head>{head}</head><body>{body}</body></html>"
    return ParsedPage(html, BASE_URL)


def _result(page: ParsedPage, check_id: str):
    results = run_meta_checks(page)
    match = next(r for r in results if r.id == check_id)
    return match


def test_run_meta_checks_returns_four_meta_results():
    results = run_meta_checks(_page())
    assert {r.id for r in results} == {
        "meta.title",
        "meta.description",
        "meta.canonical",
        "meta.robots",
    }
    assert all(r.category is CheckCategory.META for r in results)


# ---- Title ----------------------------------------------------------------


def test_title_pass():
    head = "<title>An Excellent Page About Widgets and Gadgets</title>"  # 46 chars
    r = _result(_page(head), "meta.title")
    assert r.severity is Severity.PASS
    assert r.recommendation is None


def test_title_warning_too_short():
    head = "<title>Short Title</title>"  # < 30
    r = _result(_page(head), "meta.title")
    assert r.severity is Severity.WARNING
    assert "characters" in r.message


def test_title_warning_too_long():
    head = "<title>" + ("x" * 70) + "</title>"  # > 60
    r = _result(_page(head), "meta.title")
    assert r.severity is Severity.WARNING


def test_title_fail_missing():
    r = _result(_page(""), "meta.title")
    assert r.severity is Severity.FAIL
    assert r.affected_element == "<title> missing"


# ---- Description ----------------------------------------------------------


def test_description_pass():
    desc = "x" * 100
    head = f'<meta name="description" content="{desc}">'
    r = _result(_page(head), "meta.description")
    assert r.severity is Severity.PASS
    assert r.recommendation is None


def test_description_warning_too_short():
    head = '<meta name="description" content="Too short.">'
    r = _result(_page(head), "meta.description")
    assert r.severity is Severity.WARNING


def test_description_warning_too_long():
    desc = "x" * 200
    head = f'<meta name="description" content="{desc}">'
    r = _result(_page(head), "meta.description")
    assert r.severity is Severity.WARNING


def test_description_fail_missing():
    r = _result(_page(""), "meta.description")
    assert r.severity is Severity.FAIL
    assert r.affected_element == "missing"


# ---- Canonical ------------------------------------------------------------


def test_canonical_pass():
    head = '<link rel="canonical" href="https://example.com/page">'
    r = _result(_page(head), "meta.canonical")
    assert r.severity is Severity.PASS
    assert r.affected_element == "https://example.com/page"


def test_canonical_warning_missing():
    r = _result(_page(""), "meta.canonical")
    assert r.severity is Severity.WARNING


# ---- Robots ---------------------------------------------------------------


def test_robots_pass_absent():
    r = _result(_page(""), "meta.robots")
    assert r.severity is Severity.PASS
    assert "default" in r.affected_element


def test_robots_pass_index_follow():
    head = '<meta name="robots" content="index, follow">'
    r = _result(_page(head), "meta.robots")
    assert r.severity is Severity.PASS


def test_robots_warning_nofollow():
    head = '<meta name="ROBOTS" content="index, nofollow">'  # case-insensitive name
    r = _result(_page(head), "meta.robots")
    assert r.severity is Severity.WARNING
    assert "nofollow" in r.message


def test_robots_fail_noindex():
    head = '<meta name="robots" content="NOINDEX, follow">'  # case-insensitive value
    r = _result(_page(head), "meta.robots")
    assert r.severity is Severity.FAIL
    assert "noindex" in r.message.lower()
