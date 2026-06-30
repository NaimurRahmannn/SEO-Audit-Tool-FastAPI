"""Request/response models for the audit API.

These are the wire contracts for the HTTP layer, kept separate from the core
domain schemas in ``schemas.py``.
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.schemas import AuditResult, JobStatus


class AuditRequest(BaseModel):
    """Body for POST /api/audit."""

    url: str = Field(description="The URL to audit.")
    check_broken_links: bool = Field(
        default=False,
        description="Whether to probe links for broken targets (slower).",
    )

    @field_validator("url")
    @classmethod
    def _trim_and_require(cls, value: str) -> str:
        # Light validation only; the fetcher normalizes/validates the real URL.
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("url must not be empty")
        return trimmed


class AuditJobResponse(BaseModel):
    """Serialized view of an audit job returned to the client."""

    id: str
    url: str
    status: JobStatus
    created_at: datetime
    result: AuditResult | None = None
    error: str | None = None
