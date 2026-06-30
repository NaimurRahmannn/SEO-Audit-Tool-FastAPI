"""Image SEO checks (alt-attribute coverage).

Follows the same pattern as the other check modules, but aggregates across all
images on the page: each check emits a single summary ``CheckResult`` listing a
small sample of offenders rather than one result per image.
"""

from app.audit.parser import ParsedPage
from app.models.schemas import CheckCategory, CheckResult, Severity

_SAMPLE_LIMIT = 5
_SRC_MAX_LEN = 80


def run_image_checks(page: ParsedPage) -> list[CheckResult]:
    """Run all image checks against ``page`` and return their results."""
    images = page.images()
    return [
        _check_missing_alt(images),
        _check_empty_alt(images),
    ]


def _check_missing_alt(images: list[dict]) -> CheckResult:
    total = len(images)
    offenders = [img["src"] for img in images if not img["has_alt"]]

    if offenders:
        return CheckResult(
            id="images.alt.missing",
            title="Image Alt Attributes",
            category=CheckCategory.IMAGES,
            severity=Severity.FAIL,
            message=f"{len(offenders)} of {total} images are missing an alt attribute.",
            affected_element=_sample_srcs(offenders),
            recommendation=(
                "Add descriptive alt text to every meaningful image; it aids "
                "accessibility and image SEO."
            ),
        )

    message = (
        "No images found; nothing to check."
        if total == 0
        else f"All {total} images have an alt attribute."
    )
    return CheckResult(
        id="images.alt.missing",
        title="Image Alt Attributes",
        category=CheckCategory.IMAGES,
        severity=Severity.PASS,
        message=message,
        affected_element=None,
        recommendation=None,
    )


def _check_empty_alt(images: list[dict]) -> CheckResult:
    total = len(images)
    offenders = [img["src"] for img in images if img["has_alt"] and img["alt"] == ""]

    if offenders:
        return CheckResult(
            id="images.alt.empty",
            title="Empty Image Alt Text",
            category=CheckCategory.IMAGES,
            severity=Severity.WARNING,
            message=f"{len(offenders)} of {total} images have an empty alt attribute (alt=\"\").",
            affected_element=_sample_srcs(offenders),
            recommendation=(
                "Empty alt is valid for purely decorative images; confirm these "
                "images are decorative, otherwise add descriptive alt text."
            ),
        )

    message = (
        "No images found; nothing to check."
        if total == 0
        else "No images have an empty alt attribute."
    )
    return CheckResult(
        id="images.alt.empty",
        title="Empty Image Alt Text",
        category=CheckCategory.IMAGES,
        severity=Severity.PASS,
        message=message,
        affected_element=None,
        recommendation=None,
    )


def _sample_srcs(srcs: list[str]) -> str:
    """Format up to _SAMPLE_LIMIT srcs (each truncated), noting any overflow."""
    shown = [_truncate(src) for src in srcs[:_SAMPLE_LIMIT]]
    sample = ", ".join(shown)
    extra = len(srcs) - _SAMPLE_LIMIT
    if extra > 0:
        sample += f" …(+{extra} more)"
    return sample


def _truncate(src: str | None) -> str:
    """Truncate a src to _SRC_MAX_LEN chars; represent a missing src clearly."""
    if not src:
        return "(no src)"
    if len(src) > _SRC_MAX_LEN:
        return src[:_SRC_MAX_LEN] + "…"
    return src
