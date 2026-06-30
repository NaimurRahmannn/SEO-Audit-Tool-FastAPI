"""Heading-structure SEO checks (h1 presence, hierarchy, empty headings).

Follows the same pattern as ``meta.py``: one public
``run_heading_checks(page) -> list[CheckResult]`` function plus small private
helpers, one ``CheckResult`` per check.
"""

from app.audit.parser import ParsedPage
from app.models.schemas import CheckCategory, CheckResult, Severity

# Cap the rendered outline so affected_element stays short.
_OUTLINE_CAP = 10


def run_heading_checks(page: ParsedPage) -> list[CheckResult]:
    """Run all heading checks against ``page`` and return their results."""
    headings = page.headings()

    # When there are no headings at all, emit a single dedicated check rather
    # than the H1/hierarchy/empty checks, which would be redundant.
    if not headings:
        return [_check_presence(headings)]

    return [
        _check_h1_presence(headings),
        _check_hierarchy(headings),
        _check_empty(headings),
    ]


def _check_presence(headings: list[tuple[int, str]]) -> CheckResult:
    # Only called when headings is empty.
    return CheckResult(
        id="headings.presence",
        title="Heading Structure",
        category=CheckCategory.HEADINGS,
        severity=Severity.FAIL,
        message="The page has no headings (h1–h6) at all.",
        affected_element=None,
        recommendation="Add a heading structure starting with a single <h1>.",
    )


def _check_h1_presence(headings: list[tuple[int, str]]) -> CheckResult:
    h1_texts = [text for level, text in headings if level == 1]
    count = len(h1_texts)

    if count == 0:
        return CheckResult(
            id="headings.h1.presence",
            title="H1 Heading",
            category=CheckCategory.HEADINGS,
            severity=Severity.FAIL,
            message="The page has no <h1> heading.",
            affected_element="no <h1> found",
            recommendation="Add exactly one <h1> that describes the page's main topic.",
        )

    if count > 1:
        joined = " | ".join(t or "(empty)" for t in h1_texts)
        return CheckResult(
            id="headings.h1.presence",
            title="H1 Heading",
            category=CheckCategory.HEADINGS,
            severity=Severity.WARNING,
            message=f"The page has {count} <h1> headings; a single <h1> is recommended.",
            affected_element=joined,
            recommendation="Use exactly one <h1> per page and demote the others to <h2>+.",
        )

    return CheckResult(
        id="headings.h1.presence",
        title="H1 Heading",
        category=CheckCategory.HEADINGS,
        severity=Severity.PASS,
        message="The page has exactly one <h1> heading.",
        affected_element=h1_texts[0] or "(empty)",
        recommendation=None,
    )


def _check_hierarchy(headings: list[tuple[int, str]]) -> CheckResult:
    outline = _format_outline(headings)

    # Walk in document order; flag the first jump deeper by more than one level.
    prev_level: int | None = None
    for level, _text in headings:
        if prev_level is not None and level > prev_level + 1:
            return CheckResult(
                id="headings.hierarchy",
                title="Heading Hierarchy",
                category=CheckCategory.HEADINGS,
                severity=Severity.WARNING,
                message=(
                    f"An <h{level}> follows an <h{prev_level}>, "
                    f"skipping <h{prev_level + 1}>."
                ),
                affected_element=outline,
                recommendation="Avoid skipping heading levels; increase depth one level at a time.",
            )
        prev_level = level

    return CheckResult(
        id="headings.hierarchy",
        title="Heading Hierarchy",
        category=CheckCategory.HEADINGS,
        severity=Severity.PASS,
        message="Heading levels increase without skipping.",
        affected_element=outline,
        recommendation=None,
    )


def _check_empty(headings: list[tuple[int, str]]) -> CheckResult:
    empty_levels = [level for level, text in headings if not text.strip()]

    if empty_levels:
        tags = ", ".join(f"<h{level}>" for level in empty_levels)
        count = len(empty_levels)
        plural = "heading" if count == 1 else "headings"
        return CheckResult(
            id="headings.empty",
            title="Empty Headings",
            category=CheckCategory.HEADINGS,
            severity=Severity.WARNING,
            message=f"Found {count} empty {plural} ({tags}).",
            affected_element=tags,
            recommendation="Give every heading meaningful text, or remove empty heading tags.",
        )

    return CheckResult(
        id="headings.empty",
        title="Empty Headings",
        category=CheckCategory.HEADINGS,
        severity=Severity.PASS,
        message="No empty headings were found.",
        affected_element=None,
        recommendation=None,
    )


def _format_outline(headings: list[tuple[int, str]]) -> str:
    """Render the heading outline as 'h1 > h2 > h4', capped for brevity."""
    levels = [f"h{level}" for level, _ in headings[:_OUTLINE_CAP]]
    outline = " > ".join(levels)
    if len(headings) > _OUTLINE_CAP:
        outline += " > …"
    return outline
