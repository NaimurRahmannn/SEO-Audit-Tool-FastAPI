"""Structured data SEO checks (JSON-LD).

Follows the same pattern as the other check modules. Real sites frequently ship
malformed JSON-LD, so every parse is wrapped in try/except — this module never
raises on bad input.
"""

import json

from app.audit.parser import ParsedPage
from app.models.schemas import CheckCategory, CheckResult, Severity

_TYPES_PREVIEW = 10


def run_structured_data_checks(page: ParsedPage) -> list[CheckResult]:
    """Run all structured data checks against ``page`` and return their results."""
    return [_check_json_ld(page)]


def _check_json_ld(page: ParsedPage) -> CheckResult:
    blocks = page.json_ld_blocks()
    total = len(blocks)

    parsed_ok = 0
    failed = 0
    types: set[str] = set()

    for block in blocks:
        try:
            data = json.loads(block)
        except (ValueError, TypeError):
            # ValueError covers json.JSONDecodeError; never propagate.
            failed += 1
            continue
        parsed_ok += 1
        types.update(_extract_types(data))

    discovered = sorted(types)

    # No structured data at all: recommended, not mandatory -> WARNING.
    if total == 0:
        return CheckResult(
            id="structured_data.jsonld",
            title="Structured Data (JSON-LD)",
            category=CheckCategory.STRUCTURED_DATA,
            severity=Severity.WARNING,
            message=(
                "No JSON-LD structured data found. Structured data helps search "
                "engines understand the page and can enable rich results."
            ),
            affected_element=None,
            recommendation=(
                "Add JSON-LD structured data appropriate to the content "
                "(e.g. Article, Product, Organization, BreadcrumbList)."
            ),
        )

    # Blocks exist but every one is invalid: worse than none -> FAIL.
    if parsed_ok == 0:
        return CheckResult(
            id="structured_data.jsonld",
            title="Structured Data (JSON-LD)",
            category=CheckCategory.STRUCTURED_DATA,
            severity=Severity.FAIL,
            message=(
                f"All {total} JSON-LD block(s) failed to parse. Invalid JSON-LD is "
                "ignored by search engines and signals a bug."
            ),
            affected_element=f"{failed} of {total} blocks invalid",
            recommendation="Fix the malformed JSON-LD so it is valid, parseable JSON.",
        )

    # Some valid, some broken -> WARNING.
    if failed:
        return CheckResult(
            id="structured_data.jsonld",
            title="Structured Data (JSON-LD)",
            category=CheckCategory.STRUCTURED_DATA,
            severity=Severity.WARNING,
            message=(
                f"{failed} of {total} JSON-LD block(s) failed to parse. "
                f"Detected types: {_format_types(discovered)}."
            ),
            affected_element=f"{failed} of {total} blocks invalid",
            recommendation="Fix the malformed JSON-LD block(s) so all structured data is valid.",
        )

    # All blocks valid -> PASS.
    return CheckResult(
        id="structured_data.jsonld",
        title="Structured Data (JSON-LD)",
        category=CheckCategory.STRUCTURED_DATA,
        severity=Severity.PASS,
        message=(
            f"Found {total} valid JSON-LD block(s). "
            f"Detected types: {_format_types(discovered)}."
        ),
        affected_element=_format_types(discovered) if discovered else "no @type values",
        recommendation=None,
    )


def _extract_types(data: object) -> list[str]:
    """Collect every @type string from a parsed JSON-LD value.

    Handles a single object, a top-level list of objects, an @type that is a
    string or a list, and an object with an @graph list of nodes.
    """
    nodes = data if isinstance(data, list) else [data]
    types: list[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        types.extend(_node_types(node))
        graph = node.get("@graph")
        if isinstance(graph, list):
            for graph_node in graph:
                if isinstance(graph_node, dict):
                    types.extend(_node_types(graph_node))
    return types


def _node_types(node: dict) -> list[str]:
    """Extract @type from a single dict node (string or list of strings)."""
    raw = node.get("@type")
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [t for t in raw if isinstance(t, str)]
    return []


def _format_types(types: list[str]) -> str:
    """Render the discovered type list, capped for brevity."""
    if not types:
        return "none"
    shown = ", ".join(types[:_TYPES_PREVIEW])
    extra = len(types) - _TYPES_PREVIEW
    if extra > 0:
        shown += f" …(+{extra} more)"
    return shown
