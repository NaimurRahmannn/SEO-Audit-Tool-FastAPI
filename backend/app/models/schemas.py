"""Pydantic data models for SEO audit results.

These schemas define the shape of audit data exchanged between the backend and
frontend. No audit, scoring, or persistence logic lives here — only the data
contracts.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Outcome severity of a single SEO check."""

    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class CheckCategory(str, Enum):
    """Logical grouping used to organize related checks in the UI."""

    META = "meta"
    HEADINGS = "headings"
    IMAGES = "images"
    LINKS = "links"
    SOCIAL = "social"
    STRUCTURED_DATA = "structured_data"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"


class JobStatus(str, Enum):
    """Lifecycle state of an asynchronous audit job."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class CheckResult(BaseModel):
    """Result of a single SEO check performed against a page."""

    id: str = Field(description="Stable machine key, e.g. 'meta.title.present'.")
    title: str = Field(description="Human-readable check name, e.g. 'Page Title'.")
    category: CheckCategory = Field(description="Category this check belongs to.")
    severity: Severity = Field(description="Outcome severity of the check.")
    message: str = Field(description="Clear description of what was detected.")
    affected_element: str | None = Field(
        default=None,
        description="Relevant tag, snippet, or location, when applicable.",
    )
    recommendation: str | None = Field(
        default=None,
        description="Actionable fix suggestion, when applicable.",
    )


class CategoryScore(BaseModel):
    """Aggregated score and check counts for a single category."""

    category: CheckCategory = Field(description="Category being scored.")
    score: int = Field(ge=0, le=100, description="Category score from 0 to 100.")
    passed: int = Field(ge=0, description="Number of checks that passed.")
    warnings: int = Field(ge=0, description="Number of checks that raised a warning.")
    failed: int = Field(ge=0, description="Number of checks that failed.")


class AuditResult(BaseModel):
    """Full result of auditing a single URL."""

    url: str = Field(description="The URL that was requested for audit.")
    final_url: str | None = Field(
        default=None,
        description="Resolved URL after following redirects.",
    )
    status_code: int | None = Field(
        default=None,
        description="HTTP status code of the fetched page.",
    )
    fetched_at: datetime = Field(description="When the page was fetched (UTC).")
    overall_score: int = Field(
        ge=0,
        le=100,
        description="Overall audit score from 0 to 100.",
    )
    category_scores: list[CategoryScore] = Field(
        default_factory=list,
        description="Per-category scores and counts.",
    )
    checks: list[CheckResult] = Field(
        default_factory=list,
        description="Individual check results.",
    )
    error: str | None = Field(
        default=None,
        description="Error message if the audit failed.",
    )


class AuditJob(BaseModel):
    """Tracking record for an asynchronous audit job."""

    id: str = Field(description="Unique job identifier (UUID).")
    url: str = Field(description="The URL being audited.")
    status: JobStatus = Field(description="Current lifecycle state of the job.")
    created_at: datetime = Field(description="When the job was created (UTC).")
    result: AuditResult | None = Field(
        default=None,
        description="Audit result once the job completes; None until then.",
    )
