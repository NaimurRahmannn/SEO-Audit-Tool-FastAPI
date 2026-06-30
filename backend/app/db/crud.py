"""Thin, typed CRUD helpers for audit jobs."""

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AuditJobRow


def create_job(db: Session, url: str) -> AuditJobRow:
    """Create a new audit job in the 'pending' state and return it."""
    job = AuditJobRow(id=str(uuid.uuid4()), url=url, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: str) -> AuditJobRow | None:
    """Fetch a single job by id, or None if it does not exist."""
    return db.get(AuditJobRow, job_id)


def update_job_status(
    db: Session,
    job_id: str,
    status: str,
    result_json: dict[str, Any] | None = None,
    error: str | None = None,
) -> AuditJobRow:
    """Update a job's status (and optionally its result/error) and return it.

    Raises ``ValueError`` if the job does not exist.
    """
    job = db.get(AuditJobRow, job_id)
    if job is None:
        raise ValueError(f"Audit job {job_id!r} not found")

    job.status = status
    if result_json is not None:
        job.result_json = result_json
    if error is not None:
        job.error = error

    db.commit()
    db.refresh(job)
    return job
