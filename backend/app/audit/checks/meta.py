"""Meta-tag SEO checks (title, description, canonical, robots).

This is the first check module and establishes the pattern every later module
follows: one public ``run_*_checks(page) -> list[CheckResult]`` function plus
small private helpers, one ``CheckResult`` per check.
"""

from app.audit.parser import ParsedPage
from app.models.schemas import CheckCategory, CheckResult, Severity

# Recommended length ranges (inclusive bounds for the "good" zone).
_TITLE_MIN, _TITLE_MAX = 30, 60
_DESC_MIN, _DESC_MAX = 50, 160


def run_meta_checks(page: ParsedPage) -> list[CheckResult]:
    """Run all meta-tag checks against ``page`` and return their results."""
    return [
        _check_title(page),
        _check_description(page),
        _check_canonical(page),
        _check_robots(page),
    ]


def _check_title(page: ParsedPage) -> CheckResult:
    title = page.title_text()

    if not title:
        return CheckResult(
            id="meta.title",
            title="Page Title",
            category=CheckCategory.META,
            severity=Severity.FAIL,
            message="The page has no <title> tag, or it is empty.",
            affected_element="<title> missing",
            recommendation="Add a descriptive <title> of 30–60 characters.",
        )

    length = len(title)
    if length < _TITLE_MIN or length > _TITLE_MAX:
        return CheckResult(
            id="meta.title",
            title="Page Title",
            category=CheckCategory.META,
            severity=Severity.WARNING,
            message=f"Title is {length} characters (recommended: {_TITLE_MIN}–{_TITLE_MAX}).",
            affected_element=title,
            recommendation=f"Aim for a title between {_TITLE_MIN} and {_TITLE_MAX} characters.",
        )

    return CheckResult(
        id="meta.title",
        title="Page Title",
        category=CheckCategory.META,
        severity=Severity.PASS,
        message=f"Title is present and {length} characters long.",
        affected_element=title,
        recommendation=None,
    )


def _check_description(page: ParsedPage) -> CheckResult:
    description = page.meta_content(name="description")

    if not description:
        return CheckResult(
            id="meta.description",
            title="Meta Description",
            category=CheckCategory.META,
            severity=Severity.FAIL,
            message="The page has no meta description, or it is empty.",
            affected_element="missing",
            recommendation="Add a meta description of 50–160 characters summarizing the page.",
        )

    length = len(description)
    if length < _DESC_MIN or length > _DESC_MAX:
        return CheckResult(
            id="meta.description",
            title="Meta Description",
            category=CheckCategory.META,
            severity=Severity.WARNING,
            message=f"Meta description is {length} characters "
            f"(recommended: {_DESC_MIN}–{_DESC_MAX}).",
            affected_element=description,
            recommendation=f"Aim for a description between {_DESC_MIN} and {_DESC_MAX} characters.",
        )

    return CheckResult(
        id="meta.description",
        title="Meta Description",
        category=CheckCategory.META,
        severity=Severity.PASS,
        message=f"Meta description is present and {length} characters long.",
        affected_element=description,
        recommendation=None,
    )


def _check_canonical(page: ParsedPage) -> CheckResult:
    canonical = page.canonical_href()

    if not canonical:
        return CheckResult(
            id="meta.canonical",
            title="Canonical URL",
            category=CheckCategory.META,
            severity=Severity.WARNING,
            message="No <link rel=\"canonical\"> was found.",
            affected_element=None,
            recommendation=(
                "Add a canonical link to indicate the preferred URL and avoid "
                "duplicate-content issues."
            ),
        )

    return CheckResult(
        id="meta.canonical",
        title="Canonical URL",
        category=CheckCategory.META,
        severity=Severity.PASS,
        message=f"Canonical URL is set to {canonical}.",
        affected_element=canonical,
        recommendation=None,
    )


def _check_robots(page: ParsedPage) -> CheckResult:
    robots = page.meta_content(name="robots")
    directives = robots.lower() if robots else ""

    if "noindex" in directives:
        return CheckResult(
            id="meta.robots",
            title="Robots Meta Tag",
            category=CheckCategory.META,
            severity=Severity.FAIL,
            message=f"Robots meta contains 'noindex' ('{robots}'); this page is "
            "excluded from search indexes.",
            affected_element=robots,
            recommendation="Remove 'noindex' if you want this page to appear in search results.",
        )

    if "nofollow" in directives:
        return CheckResult(
            id="meta.robots",
            title="Robots Meta Tag",
            category=CheckCategory.META,
            severity=Severity.WARNING,
            message=f"Robots meta contains 'nofollow' ('{robots}'); links on this "
            "page will not pass authority.",
            affected_element=robots,
            recommendation="Remove 'nofollow' unless you intentionally want links not to be followed.",
        )

    affected = robots if robots else "no robots meta (default: index, follow)"
    return CheckResult(
        id="meta.robots",
        title="Robots Meta Tag",
        category=CheckCategory.META,
        severity=Severity.PASS,
        message="Robots meta does not restrict indexing or link following.",
        affected_element=affected,
        recommendation=None,
    )
