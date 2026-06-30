"""Social metadata SEO checks (Open Graph, Twitter Card).

Follows the same pattern as the other check modules, but aggregates the core
tags of each protocol into a single summary ``CheckResult`` so the results list
stays proportionate. Note the attribute distinction: Open Graph tags use the
``property`` attribute, Twitter Card tags use the ``name`` attribute.
"""

from app.audit.parser import ParsedPage
from app.models.schemas import CheckCategory, CheckResult, Severity

_VALUE_MAX_LEN = 60

_OG_CORE = ["og:title", "og:description", "og:image", "og:url", "og:type"]
_TWITTER_CORE = ["twitter:card", "twitter:title", "twitter:description", "twitter:image"]


def run_social_checks(page: ParsedPage) -> list[CheckResult]:
    """Run all social metadata checks against ``page`` and return their results."""
    return [
        _check_open_graph(page),
        _check_twitter(page),
    ]


def _collect(pairs: list[tuple[str, str | None]]) -> tuple[list[tuple[str, str]], list[str]]:
    """Split (tag, value) pairs into present [(tag, value)] and missing [tag]."""
    present = [(tag, value) for tag, value in pairs if value]
    missing = [tag for tag, value in pairs if not value]
    return present, missing


def _format_present(present: list[tuple[str, str]]) -> str:
    """Render present tags as 'og:title="...", og:image="..."' with truncation."""
    return ", ".join(f'{tag}="{_truncate(value)}"' for tag, value in present)


def _truncate(value: str) -> str:
    return value if len(value) <= _VALUE_MAX_LEN else value[:_VALUE_MAX_LEN] + "…"


def _check_open_graph(page: ParsedPage) -> CheckResult:
    pairs = [(tag, page.meta_content(prop=tag)) for tag in _OG_CORE]
    present, missing = _collect(pairs)

    if not present:
        return CheckResult(
            id="social.opengraph",
            title="Open Graph Tags",
            category=CheckCategory.SOCIAL,
            severity=Severity.FAIL,
            message=(
                "No Open Graph metadata found. These tags control how the page "
                "appears when shared on social platforms (Facebook, LinkedIn, etc.)."
            ),
            affected_element="no Open Graph tags",
            recommendation=(
                "Add Open Graph tags, at minimum og:title, og:description, and og:image."
            ),
        )

    if missing:
        return CheckResult(
            id="social.opengraph",
            title="Open Graph Tags",
            category=CheckCategory.SOCIAL,
            severity=Severity.WARNING,
            message=f"Open Graph metadata is incomplete; missing: {', '.join(missing)}.",
            affected_element=_format_present(present),
            recommendation=(
                f"Add the missing Open Graph tags ({', '.join(missing)}); "
                "at minimum include og:title, og:description, and og:image."
            ),
        )

    return CheckResult(
        id="social.opengraph",
        title="Open Graph Tags",
        category=CheckCategory.SOCIAL,
        severity=Severity.PASS,
        message="All core Open Graph tags are present.",
        affected_element=_format_present(present),
        recommendation=None,
    )


def _check_twitter(page: ParsedPage) -> CheckResult:
    pairs = [(tag, page.meta_content(name=tag)) for tag in _TWITTER_CORE]
    present, missing = _collect(pairs)

    # Twitter/X falls back to Open Graph tags when a Twitter Card is absent, so
    # note that mitigation in the message when relevant (without downgrading
    # severity).
    has_og = page.meta_content(prop="og:title") is not None
    fallback_note = (
        " Twitter falls back to Open Graph tags, so this is partially mitigated."
        if has_og
        else ""
    )

    if not present:
        return CheckResult(
            id="social.twitter",
            title="Twitter Card Tags",
            category=CheckCategory.SOCIAL,
            severity=Severity.FAIL,
            message=(
                "No Twitter Card metadata found. These tags control how the page "
                "appears when shared on Twitter/X." + fallback_note
            ),
            affected_element="no Twitter Card tags",
            recommendation=(
                "Add Twitter Card tags, at minimum twitter:card, twitter:title, "
                "twitter:description, and twitter:image."
            ),
        )

    if missing:
        return CheckResult(
            id="social.twitter",
            title="Twitter Card Tags",
            category=CheckCategory.SOCIAL,
            severity=Severity.WARNING,
            message=(
                f"Twitter Card metadata is incomplete; missing: {', '.join(missing)}."
                + fallback_note
            ),
            affected_element=_format_present(present),
            recommendation=f"Add the missing Twitter Card tags ({', '.join(missing)}).",
        )

    return CheckResult(
        id="social.twitter",
        title="Twitter Card Tags",
        category=CheckCategory.SOCIAL,
        severity=Severity.PASS,
        message="All core Twitter Card tags are present.",
        affected_element=_format_present(present),
        recommendation=None,
    )
