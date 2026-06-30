"""Shared HTML parsing foundation for the audit engine.

``ParsedPage`` loads an HTML document once with BeautifulSoup and exposes a
small, reusable interface that individual SEO check modules build on. This
module deliberately contains no SEO check logic — only parsing utilities.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from app.audit.fetcher import FetchResult

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_text(value: str | None) -> str | None:
    """Collapse runs of whitespace and strip; return None if empty."""
    if value is None:
        return None
    collapsed = _WHITESPACE_RE.sub(" ", value).strip()
    return collapsed or None


class ParsedPage:
    """A parsed HTML document with convenience accessors for SEO checks."""

    def __init__(self, html: str, base_url: str) -> None:
        """Parse ``html`` with the lxml parser and remember the base URL."""
        self._soup = BeautifulSoup(html, "lxml")
        self.base_url = base_url

    @classmethod
    def from_fetch_result(cls, fetch_result: FetchResult) -> ParsedPage:
        """Build a ParsedPage from a FetchResult.

        Raises ``ValueError`` if the result has no HTML body — callers are
        responsible for checking ``fetch_result.error`` first.
        """
        if fetch_result.html is None:
            raise ValueError("FetchResult has no HTML body to parse")
        return cls(fetch_result.html, fetch_result.final_url)

    @property
    def soup(self) -> BeautifulSoup:
        """The underlying BeautifulSoup document."""
        return self._soup

    def absolute_url(self, href: str) -> str:
        """Resolve ``href`` against the page's base URL."""
        return urljoin(self.base_url, href)

    def title_text(self) -> str | None:
        """Normalized text of the first <title>, or None if absent/empty."""
        tag = self._soup.title
        if tag is None:
            return None
        return _normalize_text(tag.get_text())

    def meta_content(self, name: str | None = None, prop: str | None = None) -> str | None:
        """Return the 'content' of the first <meta> matching name or property.

        Matching is case-insensitive. Pass ``name`` (e.g. "description",
        "robots") or ``prop`` (e.g. "og:title"); the first match wins.
        """
        wanted_name = name.lower() if name else None
        wanted_prop = prop.lower() if prop else None

        for meta in self._soup.find_all("meta"):
            meta_name = meta.get("name")
            meta_prop = meta.get("property")
            if wanted_name and meta_name and meta_name.lower() == wanted_name:
                return _strip_attr(meta.get("content"))
            if wanted_prop and meta_prop and meta_prop.lower() == wanted_prop:
                return _strip_attr(meta.get("content"))
        return None

    def all_meta(self) -> list[dict]:
        """Every <meta> tag as {name, property, content} (for coverage/debug)."""
        result: list[dict] = []
        for meta in self._soup.find_all("meta"):
            result.append(
                {
                    "name": meta.get("name"),
                    "property": meta.get("property"),
                    "content": meta.get("content"),
                }
            )
        return result

    def headings(self) -> list[tuple[int, str]]:
        """Ordered (level, text) pairs for every h1..h6 in document order."""
        result: list[tuple[int, str]] = []
        for tag in self._soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            level = int(tag.name[1])
            text = _normalize_text(tag.get_text()) or ""
            result.append((level, text))
        return result

    def links(self) -> list[dict]:
        """Every <a href> as {href, text, rel, is_internal}.

        ``href`` is the raw attribute value; ``is_internal`` compares the
        resolved absolute host against the base URL host.
        """
        base_host = urlparse(self.base_url).netloc.lower()
        result: list[dict] = []
        for a in self._soup.find_all("a", href=True):
            href = a.get("href")
            rel = a.get("rel")  # bs4 returns a list for rel, or None
            resolved_host = urlparse(urljoin(self.base_url, href)).netloc.lower()
            result.append(
                {
                    "href": href,
                    "text": _normalize_text(a.get_text()),
                    "rel": rel,
                    "is_internal": resolved_host == base_host,
                }
            )
        return result

    def images(self) -> list[dict]:
        """Every <img> as {src, alt, has_alt}.

        ``alt`` is None when the attribute is absent and "" when present but
        empty; ``has_alt`` reflects attribute presence.
        """
        result: list[dict] = []
        for img in self._soup.find_all("img"):
            has_alt = img.has_attr("alt")
            alt = img.get("alt") if has_alt else None
            result.append(
                {
                    "src": img.get("src"),
                    "alt": alt,
                    "has_alt": has_alt,
                }
            )
        return result

    def canonical_href(self) -> str | None:
        """Href of <link rel="canonical">, or None if absent."""
        link = self._soup.find("link", rel="canonical")
        if link is None:
            return None
        return _strip_attr(link.get("href"))

    def json_ld_blocks(self) -> list[str]:
        """Raw text of every <script type="application/ld+json"> block."""
        blocks: list[str] = []
        for script in self._soup.find_all("script", attrs={"type": "application/ld+json"}):
            text = script.string if script.string is not None else script.get_text()
            if text and text.strip():
                blocks.append(text.strip())
        return blocks


def _strip_attr(value: str | None) -> str | None:
    """Strip an attribute value, returning None when missing or empty."""
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
