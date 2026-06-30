"""Tests for app.audit.checks.images.run_image_checks."""

from app.audit.checks.images import run_image_checks
from app.audit.parser import ParsedPage
from app.models.schemas import CheckCategory, Severity

BASE_URL = "https://example.com/"


def _page(body: str) -> ParsedPage:
    html = f"<!DOCTYPE html><html><head></head><body>{body}</body></html>"
    return ParsedPage(html, BASE_URL)


def _result(page: ParsedPage, check_id: str):
    return next(r for r in run_image_checks(page) if r.id == check_id)


def test_all_results_are_images_category():
    page = _page('<img src="/a.png" alt="A">')
    assert all(r.category is CheckCategory.IMAGES for r in run_image_checks(page))


# ---- Missing alt ----------------------------------------------------------


def test_missing_alt_pass_all_have_alt():
    body = '<img src="/a.png" alt="A"><img src="/b.png" alt="">'
    r = _result(_page(body), "images.alt.missing")
    assert r.severity is Severity.PASS
    assert r.recommendation is None


def test_missing_alt_fail_with_count():
    body = '<img src="/a.png" alt="A"><img src="/b.png"><img src="/c.png">'
    r = _result(_page(body), "images.alt.missing")
    assert r.severity is Severity.FAIL
    assert "2 of 3" in r.message
    assert "/b.png" in r.affected_element and "/c.png" in r.affected_element


# ---- Empty alt ------------------------------------------------------------


def test_empty_alt_warning():
    body = '<img src="/a.png" alt="A"><img src="/b.png" alt="">'
    r = _result(_page(body), "images.alt.empty")
    assert r.severity is Severity.WARNING
    assert "1 of 2" in r.message
    assert "/b.png" in r.affected_element


def test_empty_alt_pass_when_none_empty():
    body = '<img src="/a.png" alt="A">'
    r = _result(_page(body), "images.alt.empty")
    assert r.severity is Severity.PASS


# ---- No images ------------------------------------------------------------


def test_no_images_both_pass():
    results = run_image_checks(_page("<p>no images</p>"))
    assert {r.severity for r in results} == {Severity.PASS}
    for r in results:
        assert "No images found" in r.message
        assert r.affected_element is None


# ---- Sampling / truncation ------------------------------------------------


def test_missing_alt_sample_caps_at_five_with_overflow():
    # 7 images all missing alt -> sample shows 5 + "(+2 more)".
    body = "".join(f'<img src="/img{i}.png">' for i in range(7))
    r = _result(_page(body), "images.alt.missing")
    assert r.severity is Severity.FAIL
    assert "7 of 7" in r.message
    assert "…(+2 more)" in r.affected_element
    # Exactly 5 srcs listed before the overflow marker.
    sample_part = r.affected_element.split(" …(+")[0]
    assert sample_part.count("/img") == 5


def test_long_src_is_truncated():
    long_src = "/" + ("x" * 200) + ".png"
    body = f'<img src="{long_src}">'
    r = _result(_page(body), "images.alt.missing")
    assert "…" in r.affected_element
    # Truncated to 80 chars + ellipsis, so far shorter than the original.
    assert len(r.affected_element) < len(long_src)
