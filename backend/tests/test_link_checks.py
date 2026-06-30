"""Tests for app.audit.checks.links.run_link_checks."""

import httpx
import pytest
import respx

from app.audit.checks.links import run_link_checks
from app.audit.parser import ParsedPage
from app.models.schemas import CheckCategory, Severity

BASE_URL = "https://example.com/"


def _page(body: str) -> ParsedPage:
    html = f"<!DOCTYPE html><html><head></head><body>{body}</body></html>"
    return ParsedPage(html, BASE_URL)


def _by_id(results, check_id):
    return next((r for r in results if r.id == check_id), None)


# ---- Inventory ------------------------------------------------------------


@pytest.mark.asyncio
async def test_inventory_counts_only_navigational():
    body = """
    <a href="/about">About</a>
    <a href="https://example.com/contact">Contact</a>
    <a href="https://other.com/x">External</a>
    <a href="mailto:hi@example.com">Email</a>
    <a href="tel:+123">Call</a>
    <a href="javascript:void(0)">JS</a>
    <a href="#">Top</a>
    <a href="">Empty</a>
    """
    results = await run_link_checks(_page(body))
    inv = _by_id(results, "links.inventory")
    assert inv.severity is Severity.PASS
    # 3 navigational: /about (internal), example.com/contact (internal), other.com (external)
    assert inv.message == "3 links found (2 internal, 1 external)."
    assert all(r.category is CheckCategory.LINKS for r in results)


@pytest.mark.asyncio
async def test_inventory_zero_links_warning():
    body = '<a href="mailto:x@y.com">Mail</a><a href="#">Top</a>'
    results = await run_link_checks(_page(body))
    inv = _by_id(results, "links.inventory")
    assert inv.severity is Severity.WARNING


# ---- External rel ---------------------------------------------------------


@pytest.mark.asyncio
async def test_external_rel_reporting():
    body = """
    <a href="https://other.com/a" rel="nofollow">A</a>
    <a href="https://other.com/b" rel="sponsored ugc">B</a>
    <a href="https://other.com/c">C</a>
    <a href="/internal">Internal</a>
    """
    results = await run_link_checks(_page(body))
    rel = _by_id(results, "links.external.rel")
    assert rel.severity is Severity.PASS
    assert rel.message == "3 external links, 2 marked nofollow/sponsored/ugc."


@pytest.mark.asyncio
async def test_external_rel_no_external():
    results = await run_link_checks(_page('<a href="/internal">x</a>'))
    rel = _by_id(results, "links.external.rel")
    assert rel.severity is Severity.PASS
    assert rel.message == "No external links."


# ---- Broken links: omitted unless requested -------------------------------


@pytest.mark.asyncio
async def test_broken_omitted_by_default():
    results = await run_link_checks(_page('<a href="/a">a</a>'))
    assert _by_id(results, "links.broken") is None


# ---- Broken links: detection ----------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_broken_detection_mixed():
    body = """
    <a href="/good">good</a>
    <a href="/missing">missing</a>
    <a href="https://other.com/slow">slow</a>
    """
    respx.head("https://example.com/good").mock(return_value=httpx.Response(200))
    respx.head("https://example.com/missing").mock(return_value=httpx.Response(404))
    respx.head("https://other.com/slow").mock(side_effect=httpx.ConnectTimeout("slow"))

    results = await run_link_checks(_page(body), check_broken=True)
    broken = _by_id(results, "links.broken")
    assert broken.severity is Severity.FAIL
    assert "2 of 3 checked links are broken" in broken.message
    assert "https://example.com/missing (404)" in broken.affected_element
    assert "https://other.com/slow (timeout)" in broken.affected_element


@pytest.mark.asyncio
@respx.mock
async def test_broken_all_reachable_pass():
    body = '<a href="/a">a</a><a href="/b">b</a>'
    respx.head("https://example.com/a").mock(return_value=httpx.Response(200))
    respx.head("https://example.com/b").mock(return_value=httpx.Response(301))  # redirect ok

    results = await run_link_checks(_page(body), check_broken=True)
    broken = _by_id(results, "links.broken")
    assert broken.severity is Severity.PASS
    assert "All 2 checked links are reachable" in broken.message


@pytest.mark.asyncio
@respx.mock
async def test_broken_head_405_falls_back_to_get():
    respx.head("https://example.com/h").mock(return_value=httpx.Response(405))
    respx.get("https://example.com/h").mock(return_value=httpx.Response(200))

    results = await run_link_checks(_page('<a href="/h">h</a>'), check_broken=True)
    broken = _by_id(results, "links.broken")
    assert broken.severity is Severity.PASS


# ---- Broken links: cap ----------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_broken_caps_at_30():
    # 35 distinct internal links; all reachable.
    body = "".join(f'<a href="/p{i}">p{i}</a>' for i in range(35))
    respx.route(method="HEAD").mock(return_value=httpx.Response(200))

    results = await run_link_checks(_page(body), check_broken=True)
    broken = _by_id(results, "links.broken")
    assert broken.severity is Severity.PASS
    assert "All 30 checked links are reachable" in broken.message
    assert "Checked first 30 of 35" in broken.message
