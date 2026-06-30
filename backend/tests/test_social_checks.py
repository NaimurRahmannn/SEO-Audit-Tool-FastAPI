"""Tests for app.audit.checks.social.run_social_checks."""

from app.audit.checks.social import run_social_checks
from app.audit.parser import ParsedPage
from app.models.schemas import CheckCategory, Severity

BASE_URL = "https://example.com/"

_OG_ALL = """
<meta property="og:title" content="Title">
<meta property="og:description" content="Desc">
<meta property="og:image" content="https://example.com/i.png">
<meta property="og:url" content="https://example.com/">
<meta property="og:type" content="website">
"""

_TWITTER_ALL = """
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Title">
<meta name="twitter:description" content="Desc">
<meta name="twitter:image" content="https://example.com/i.png">
"""


def _page(head: str) -> ParsedPage:
    html = f"<!DOCTYPE html><html><head>{head}</head><body></body></html>"
    return ParsedPage(html, BASE_URL)


def _result(page: ParsedPage, check_id: str):
    return next(r for r in run_social_checks(page) if r.id == check_id)


def test_all_results_are_social_category():
    page = _page(_OG_ALL + _TWITTER_ALL)
    assert all(r.category is CheckCategory.SOCIAL for r in run_social_checks(page))


# ---- Open Graph -----------------------------------------------------------


def test_og_pass_all_present():
    r = _result(_page(_OG_ALL), "social.opengraph")
    assert r.severity is Severity.PASS
    assert r.recommendation is None
    assert "og:title" in r.affected_element


def test_og_warning_partial_lists_missing():
    head = """
    <meta property="og:title" content="Title">
    <meta property="og:description" content="Desc">
    """
    r = _result(_page(head), "social.opengraph")
    assert r.severity is Severity.WARNING
    assert "og:image" in r.message
    assert "og:url" in r.message
    assert "og:type" in r.message


def test_og_fail_none_present():
    r = _result(_page(""), "social.opengraph")
    assert r.severity is Severity.FAIL
    assert r.affected_element == "no Open Graph tags"


# ---- Twitter Card ---------------------------------------------------------


def test_twitter_pass_all_present():
    r = _result(_page(_TWITTER_ALL), "social.twitter")
    assert r.severity is Severity.PASS
    assert r.recommendation is None


def test_twitter_warning_partial():
    head = """
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="Title">
    """
    r = _result(_page(head), "social.twitter")
    assert r.severity is Severity.WARNING
    assert "twitter:description" in r.message
    assert "twitter:image" in r.message


def test_twitter_fail_none_present():
    r = _result(_page(""), "social.twitter")
    assert r.severity is Severity.FAIL
    assert r.affected_element == "no Twitter Card tags"
    # No OG either, so no fallback note.
    assert "falls back" not in r.message


# ---- Twitter falls back to OG ---------------------------------------------


def test_twitter_fail_mentions_og_fallback_when_og_present():
    # OG present but no Twitter tags -> fallback note should appear.
    r = _result(_page(_OG_ALL), "social.twitter")
    assert r.severity is Severity.FAIL
    assert "falls back to Open Graph" in r.message


def test_twitter_warning_mentions_og_fallback_when_og_present():
    head = _OG_ALL + '<meta name="twitter:card" content="summary">'
    r = _result(_page(head), "social.twitter")
    assert r.severity is Severity.WARNING
    assert "falls back to Open Graph" in r.message
