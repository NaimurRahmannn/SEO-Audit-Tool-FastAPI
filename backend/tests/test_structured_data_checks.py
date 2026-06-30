"""Tests for app.audit.checks.structured_data.run_structured_data_checks."""

from app.audit.checks.structured_data import run_structured_data_checks
from app.audit.parser import ParsedPage
from app.models.schemas import CheckCategory, Severity

BASE_URL = "https://example.com/"


def _page_with_scripts(*blocks: str) -> ParsedPage:
    scripts = "".join(
        f'<script type="application/ld+json">{b}</script>' for b in blocks
    )
    html = f"<!DOCTYPE html><html><head>{scripts}</head><body></body></html>"
    return ParsedPage(html, BASE_URL)


def _only(page: ParsedPage):
    results = run_structured_data_checks(page)
    assert len(results) == 1
    return results[0]


def test_category_and_id():
    r = _only(_page_with_scripts('{"@type": "Article"}'))
    assert r.category is CheckCategory.STRUCTURED_DATA
    assert r.id == "structured_data.jsonld"


def test_no_blocks_is_warning():
    page = ParsedPage("<html><head></head><body></body></html>", BASE_URL)
    r = _only(page)
    assert r.severity is Severity.WARNING
    assert r.affected_element is None


def test_single_object_pass_with_type():
    r = _only(_page_with_scripts('{"@type": "Article", "headline": "Hi"}'))
    assert r.severity is Severity.PASS
    assert "Article" in r.affected_element


def test_type_as_list():
    r = _only(_page_with_scripts('{"@type": ["Article", "NewsArticle"]}'))
    assert r.severity is Severity.PASS
    assert "Article" in r.affected_element
    assert "NewsArticle" in r.affected_element


def test_top_level_list_of_objects():
    block = '[{"@type": "Organization"}, {"@type": "WebSite"}]'
    r = _only(_page_with_scripts(block))
    assert r.severity is Severity.PASS
    # Sorted, de-duplicated.
    assert "Organization" in r.affected_element
    assert "WebSite" in r.affected_element


def test_graph_nodes():
    block = '{"@graph": [{"@type": "Person"}, {"@type": "BreadcrumbList"}]}'
    r = _only(_page_with_scripts(block))
    assert r.severity is Severity.PASS
    assert "BreadcrumbList" in r.affected_element
    assert "Person" in r.affected_element


def test_types_are_sorted_and_deduplicated():
    r = _only(
        _page_with_scripts('{"@type": "WebSite"}', '{"@type": "Article"}', '{"@type": "Article"}')
    )
    assert r.severity is Severity.PASS
    # Article should appear once and before WebSite (sorted).
    types_part = r.affected_element
    assert types_part.index("Article") < types_part.index("WebSite")
    assert types_part.count("Article") == 1


def test_all_invalid_is_fail():
    r = _only(_page_with_scripts("{not valid json", "also bad}"))
    assert r.severity is Severity.FAIL
    assert "2 of 2" in r.affected_element


def test_partial_invalid_is_warning():
    r = _only(_page_with_scripts('{"@type": "Article"}', "{broken"))
    assert r.severity is Severity.WARNING
    assert "1 of 2" in r.message
    assert "Article" in r.message


def test_malformed_json_never_raises():
    # Sanity: a variety of garbage inputs must not raise.
    r = _only(_page_with_scripts("", "null", "12345", '{"@type": 99}', "[1, 2, 3]"))
    # All parse as valid JSON except the empty string (which fails);
    # none should raise regardless of severity.
    assert r.id == "structured_data.jsonld"
