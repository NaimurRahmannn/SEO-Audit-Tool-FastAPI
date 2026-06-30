"""Tests for app.audit.parser.ParsedPage using a small sample document."""

import pytest

from app.audit.fetcher import FetchResult
from app.audit.parser import ParsedPage

BASE_URL = "https://example.com/blog/post"

SAMPLE_HTML = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>  Hello   World  </title>
    <meta name="Description" content="  A sample page.  ">
    <meta name="robots" content="index,follow">
    <meta property="og:title" content="OG Hello">
    <link rel="canonical" href="https://example.com/blog/post">
    <script type="application/ld+json">{"@type": "Article"}</script>
  </head>
  <body>
    <h1>Main   Heading</h1>
    <h2>Sub</h2>
    <h3></h3>
    <a href="/about">About</a>
    <a href="https://example.com/contact">Contact</a>
    <a href="https://other.com/x" rel="nofollow">External</a>
    <img src="/a.png" alt="A picture">
    <img src="/b.png" alt="">
    <img src="/c.png">
  </body>
</html>
"""


@pytest.fixture
def page() -> ParsedPage:
    return ParsedPage(SAMPLE_HTML, BASE_URL)


def test_from_fetch_result_builds_page():
    fr = FetchResult(
        requested_url=BASE_URL,
        final_url=BASE_URL,
        status_code=200,
        html=SAMPLE_HTML,
    )
    page = ParsedPage.from_fetch_result(fr)
    assert page.base_url == BASE_URL
    assert page.title_text() == "Hello World"


def test_from_fetch_result_raises_without_html():
    fr = FetchResult(requested_url=BASE_URL, final_url=BASE_URL, html=None)
    with pytest.raises(ValueError):
        ParsedPage.from_fetch_result(fr)


def test_title_text_is_normalized(page: ParsedPage):
    assert page.title_text() == "Hello World"


def test_title_text_none_when_absent():
    page = ParsedPage("<html><head></head><body></body></html>", BASE_URL)
    assert page.title_text() is None


def test_meta_content_by_name_case_insensitive(page: ParsedPage):
    # Attribute is "Description"; lookup is case-insensitive and value stripped.
    assert page.meta_content(name="description") == "A sample page."
    assert page.meta_content(name="robots") == "index,follow"


def test_meta_content_by_property(page: ParsedPage):
    assert page.meta_content(prop="og:title") == "OG Hello"


def test_meta_content_missing_returns_none(page: ParsedPage):
    assert page.meta_content(name="keywords") is None


def test_all_meta_lists_tags(page: ParsedPage):
    metas = page.all_meta()
    assert {"name": "robots", "property": None, "content": "index,follow"} in metas
    assert any(m["property"] == "og:title" for m in metas)


def test_headings_in_order(page: ParsedPage):
    assert page.headings() == [(1, "Main Heading"), (2, "Sub"), (3, "")]


def test_links_internal_external_and_resolution(page: ParsedPage):
    links = page.links()
    by_href = {link["href"]: link for link in links}

    assert by_href["/about"]["is_internal"] is True
    assert by_href["https://example.com/contact"]["is_internal"] is True
    assert by_href["https://other.com/x"]["is_internal"] is False
    assert by_href["https://other.com/x"]["rel"] == ["nofollow"]
    assert by_href["/about"]["text"] == "About"


def test_images_alt_handling(page: ParsedPage):
    images = page.images()
    by_src = {img["src"]: img for img in images}

    # Present, non-empty alt
    assert by_src["/a.png"] == {"src": "/a.png", "alt": "A picture", "has_alt": True}
    # Present but empty alt
    assert by_src["/b.png"] == {"src": "/b.png", "alt": "", "has_alt": True}
    # Missing alt attribute
    assert by_src["/c.png"] == {"src": "/c.png", "alt": None, "has_alt": False}


def test_canonical_href(page: ParsedPage):
    assert page.canonical_href() == "https://example.com/blog/post"


def test_json_ld_blocks(page: ParsedPage):
    blocks = page.json_ld_blocks()
    assert blocks == ['{"@type": "Article"}']


def test_absolute_url(page: ParsedPage):
    assert page.absolute_url("/about") == "https://example.com/about"
    assert page.absolute_url("../x") == "https://example.com/x"
