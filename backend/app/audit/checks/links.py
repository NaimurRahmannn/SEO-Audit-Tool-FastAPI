"""Link SEO checks (inventory, external rel, optional broken-link probing).

Follows the same pattern as the other check modules, with two differences:
the parse-only checks are synchronous logic, but the public entry point is
async because it optionally awaits a network-bound broken-link check. That
check is bounded (concurrency + a hard cap) so an audit can't hang on a
link-heavy page, and it never raises — a link that errors is simply "broken".
"""

import asyncio

import httpx

from app.audit.parser import ParsedPage
from app.models.schemas import CheckCategory, CheckResult, Severity

# Hrefs with these prefixes (or the exact values "" / "#") are not navigational.
_NON_NAV_PREFIXES = ("mailto:", "tel:", "javascript:")

_REL_FLAGS = {"nofollow", "sponsored", "ugc"}

# Broken-link probing limits.
_MAX_BROKEN_CHECKS = 30
_CONCURRENCY = 8
_REQUEST_TIMEOUT = httpx.Timeout(8.0)
_BROKEN_SAMPLE_LIMIT = 5


async def run_link_checks(page: ParsedPage, check_broken: bool = False) -> list[CheckResult]:
    """Run link checks against ``page``.

    The broken-link check (network-bound) is only included when
    ``check_broken`` is True.
    """
    links = page.links()
    nav_links = [link for link in links if _is_navigational(link["href"])]

    results = [
        _check_inventory(nav_links),
        _check_external_rel(nav_links),
    ]
    if check_broken:
        results.append(await _check_broken_links(page, nav_links))
    return results


def _is_navigational(href: str | None) -> bool:
    """True for http/https/relative links; False for empty, '#', mailto/tel/js."""
    if not href:
        return False
    cleaned = href.strip()
    if not cleaned or cleaned == "#":
        return False
    if cleaned.lower().startswith(_NON_NAV_PREFIXES):
        return False
    return True


def _check_inventory(nav_links: list[dict]) -> CheckResult:
    total = len(nav_links)
    internal = sum(1 for link in nav_links if link["is_internal"])
    external = total - internal

    if total == 0:
        return CheckResult(
            id="links.inventory",
            title="Link Inventory",
            category=CheckCategory.LINKS,
            severity=Severity.WARNING,
            message="No navigational links found on the page.",
            affected_element=None,
            recommendation=(
                "Add links to other pages so users and search engines can crawl "
                "the site."
            ),
        )

    return CheckResult(
        id="links.inventory",
        title="Link Inventory",
        category=CheckCategory.LINKS,
        severity=Severity.PASS,
        message=f"{total} links found ({internal} internal, {external} external).",
        affected_element=None,
        recommendation=None,
    )


def _check_external_rel(nav_links: list[dict]) -> CheckResult:
    external = [link for link in nav_links if not link["is_internal"]]

    if not external:
        return CheckResult(
            id="links.external.rel",
            title="External Link Attributes",
            category=CheckCategory.LINKS,
            severity=Severity.PASS,
            message="No external links.",
            affected_element=None,
            recommendation=None,
        )

    flagged = sum(1 for link in external if _has_rel_flag(link["rel"]))
    return CheckResult(
        id="links.external.rel",
        title="External Link Attributes",
        category=CheckCategory.LINKS,
        severity=Severity.PASS,
        message=(
            f"{len(external)} external links, {flagged} marked nofollow/sponsored/ugc."
        ),
        affected_element=None,
        recommendation=None,
    )


def _has_rel_flag(rel: list[str] | None) -> bool:
    """True if a link's rel list contains nofollow/sponsored/ugc."""
    if not rel:
        return False
    return any(value.lower() in _REL_FLAGS for value in rel)


async def _check_broken_links(page: ParsedPage, nav_links: list[dict]) -> CheckResult:
    # Resolve to absolute URLs and de-duplicate, preserving first-seen order.
    seen: set[str] = set()
    urls: list[str] = []
    for link in nav_links:
        absolute = page.absolute_url(link["href"])
        if absolute not in seen:
            seen.add(absolute)
            urls.append(absolute)

    total_unique = len(urls)
    if total_unique == 0:
        return CheckResult(
            id="links.broken",
            title="Broken Links",
            category=CheckCategory.LINKS,
            severity=Severity.PASS,
            message="No navigational links to check.",
            affected_element=None,
            recommendation=None,
        )

    # Hard cap so a link-heavy page can't make the audit hang.
    to_check = urls[:_MAX_BROKEN_CHECKS]
    semaphore = asyncio.Semaphore(_CONCURRENCY)

    async with httpx.AsyncClient(follow_redirects=True, timeout=_REQUEST_TIMEOUT) as client:
        probes = [_probe_url(client, semaphore, url) for url in to_check]
        results = await asyncio.gather(*probes)

    broken = [(url, label) for url, ok, label in results if not ok]
    checked = len(to_check)
    cap_note = (
        f" (Checked first {_MAX_BROKEN_CHECKS} of {total_unique}.)"
        if total_unique > _MAX_BROKEN_CHECKS
        else ""
    )

    if broken:
        return CheckResult(
            id="links.broken",
            title="Broken Links",
            category=CheckCategory.LINKS,
            severity=Severity.FAIL,
            message=f"{len(broken)} of {checked} checked links are broken.{cap_note}",
            affected_element=_sample_broken(broken),
            recommendation="Fix or remove the broken links.",
        )

    return CheckResult(
        id="links.broken",
        title="Broken Links",
        category=CheckCategory.LINKS,
        severity=Severity.PASS,
        message=f"All {checked} checked links are reachable.{cap_note}",
        affected_element=None,
        recommendation=None,
    )


async def _probe_url(
    client: httpx.AsyncClient, semaphore: asyncio.Semaphore, url: str
) -> tuple[str, bool, str]:
    """Probe one URL. Returns (url, is_ok, label) and never raises."""
    async with semaphore:
        try:
            response = await client.head(url)
            # Some servers reject HEAD; retry with GET before judging.
            if response.status_code == 405:
                response = await client.get(url)
        except httpx.TimeoutException:
            return (url, False, "timeout")
        except httpx.RequestError:
            return (url, False, "error")

    if response.status_code >= 400:
        return (url, False, str(response.status_code))
    return (url, True, str(response.status_code))


def _sample_broken(broken: list[tuple[str, str]]) -> str:
    """Format up to _BROKEN_SAMPLE_LIMIT broken links as 'url (label)'."""
    shown = [f"{url} ({label})" for url, label in broken[:_BROKEN_SAMPLE_LIMIT]]
    sample = ", ".join(shown)
    extra = len(broken) - _BROKEN_SAMPLE_LIMIT
    if extra > 0:
        sample += f" …(+{extra} more)"
    return sample
