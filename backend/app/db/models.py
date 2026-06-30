"""SQLAlchemy ORM models (database tables)."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

# JSONB on PostgreSQL (production), generic JSON elsewhere (e.g. SQLite in tests).
_JSONType = JSONB().with_variant(JSON(), "sqlite")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditJobRow(Base):
    """Persistent record tracking the lifecycle of an audit job."""

    __tablename__ = "audit_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )
    result_json: Mapped[dict[str, Any] | None] = mapped_column(_JSONType, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
