"""HTTP fetch layer for the SEO audit engine.

Fetches a target URL with httpx, following redirects, and returns a structured
``FetchResult``. Network/transport failures are converted into a result with
``error`` set — this function never raises to the caller.
"""

import time
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, Field

# A realistic User-Agent so servers treat us like a normal crawler, plus an
# Accept header that prefers HTML.
_HEADERS = {
    "User-Agent": "SEOAuditBot/1.0 (+https://example.com)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Total budget split across connect/read/write/pool phases.
_TIMEOUT = httpx.Timeout(15.0)


class FetchResult(BaseModel):
    """Outcome of fetching a single URL over HTTP."""

    requested_url: str = Field(description="The URL as requested (after normalization).")
    final_url: str = Field(description="The resolved URL after following redirects.")
    status_code: int | None = Field(default=None, description="HTTP status code, if received.")
    html: str | None = Field(default=None, description="Response body if it was HTML, else None.")
    content_type: str | None = Field(default=None, description="Raw Content-Type header value.")
    elapsed_ms: int = Field(default=0, description="Wall-clock fetch duration in milliseconds.")
    error: str | None = Field(default=None, description="Error message if the fetch failed.")


def normalize_url(url: str) -> str:
    """Trim whitespace and prepend 'https://' when no scheme is present."""
    cleaned = url.strip()
    # urlsplit only detects a scheme when '://' is present for our purposes;
    # treat a missing scheme as https.
    if "://" not in cleaned:
        cleaned = f"https://{cleaned}"
    return cleaned


async def fetch_page(url: str) -> FetchResult:
    """Fetch ``url`` and return a ``FetchResult``; never raises to the caller."""
    requested_url = normalize_url(url)

    # Reject obviously invalid URLs (missing host, or a host containing
    # whitespace) before hitting the network.
    parts = urlsplit(requested_url)
    if not parts.netloc or any(ch.isspace() for ch in parts.netloc):
        return FetchResult(
            requested_url=requested_url,
            final_url=requested_url,
            error="Invalid URL",
        )

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=_TIMEOUT,
            headers=_HEADERS,
        ) as client:
            response = await client.get(requested_url)
    except httpx.TimeoutException:
        return _failure(requested_url, start, "Request timed out")
    except httpx.ConnectError:
        return _failure(requested_url, start, "Could not connect to the host")
    except httpx.InvalidURL:
        return _failure(requested_url, start, "Invalid URL")
    except httpx.RequestError as exc:
        # Any other transport-level error (DNS, TLS, too many redirects, etc.).
        return _failure(requested_url, start, f"Request failed: {exc.__class__.__name__}")

    elapsed_ms = _elapsed_ms(start)

    # Only bodies served as text/html are parseable; for PDFs, images, JSON,
    # etc. we keep the status/content-type but leave html=None.
    content_type = response.headers.get("content-type")
    is_html = content_type is not None and "text/html" in content_type.lower()

    # A 4xx/5xx is a successful fetch from our perspective: we return the status
    # code (and HTML body if present) without setting `error`, so downstream
    # checks can report on it.
    return FetchResult(
        requested_url=requested_url,
        final_url=str(response.url),
        status_code=response.status_code,
        html=response.text if is_html else None,
        content_type=content_type,
        elapsed_ms=elapsed_ms,
    )


def _elapsed_ms(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)


def _failure(requested_url: str, start: float, message: str) -> FetchResult:
    """Build a failed FetchResult preserving elapsed time."""
    return FetchResult(
        requested_url=requested_url,
        final_url=requested_url,
        elapsed_ms=_elapsed_ms(start),
        error=message,
    )
