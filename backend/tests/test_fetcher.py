"""Tests for app.audit.fetcher. No real network calls — httpx is mocked."""

import httpx
import pytest
import respx

from app.audit.fetcher import fetch_page, normalize_url


def test_normalize_url_adds_scheme():
    assert normalize_url("example.com") == "https://example.com"
    assert normalize_url("  example.com  ") == "https://example.com"
    # Existing scheme is preserved.
    assert normalize_url("http://example.com") == "http://example.com"


@pytest.mark.asyncio
@respx.mock
async def test_successful_html_response():
    html = "<html><head><title>Hi</title></head><body>ok</body></html>"
    respx.get("https://example.com").mock(
        return_value=httpx.Response(
            200, html=html, headers={"content-type": "text/html; charset=utf-8"}
        )
    )

    result = await fetch_page("example.com")  # scheme-less input is normalized

    assert result.error is None
    assert result.status_code == 200
    assert result.requested_url == "https://example.com"
    assert result.final_url == "https://example.com"
    assert result.html == html
    assert result.content_type is not None and "text/html" in result.content_type


@pytest.mark.asyncio
@respx.mock
async def test_non_html_response_has_no_html():
    respx.get("https://example.com/data.json").mock(
        return_value=httpx.Response(
            200, json={"k": "v"}, headers={"content-type": "application/json"}
        )
    )

    result = await fetch_page("https://example.com/data.json")

    assert result.error is None
    assert result.status_code == 200
    assert result.html is None
    assert result.content_type == "application/json"


@pytest.mark.asyncio
@respx.mock
async def test_http_error_status_is_not_an_error():
    respx.get("https://example.com/missing").mock(
        return_value=httpx.Response(404, headers={"content-type": "text/html"})
    )

    result = await fetch_page("https://example.com/missing")

    # 4xx is a successful fetch: status returned, error stays None.
    assert result.status_code == 404
    assert result.error is None


@pytest.mark.asyncio
@respx.mock
async def test_timeout_is_handled():
    respx.get("https://example.com").mock(side_effect=httpx.ReadTimeout("timed out"))

    result = await fetch_page("https://example.com")

    assert result.status_code is None
    assert result.error == "Request timed out"


@pytest.mark.asyncio
@respx.mock
async def test_connection_error_is_handled():
    respx.get("https://example.com").mock(side_effect=httpx.ConnectError("refused"))

    result = await fetch_page("https://example.com")

    assert result.status_code is None
    assert result.error == "Could not connect to the host"


@pytest.mark.asyncio
async def test_invalid_url_missing_host():
    result = await fetch_page("not a url")

    # No netloc -> rejected before any network call.
    assert result.error == "Invalid URL"
    assert result.status_code is None
