"""Audit API endpoints (async job pattern, all under /api)."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.worker import run_audit_job
from app.db import crud
from app.db.models import AuditJobRow
from app.db.session import get_db
from app.models.api_schemas import AuditJobResponse, AuditRequest
from app.models.schemas import AuditResult, JobStatus

router = APIRouter(prefix="/api", tags=["audit"])


def _to_response(job: AuditJobRow) -> AuditJobResponse:
    """Map a DB row to the API response, deserializing the result when done."""
    result = None
    if job.status == JobStatus.DONE.value and job.result_json:
        result = AuditResult.model_validate(job.result_json)

    return AuditJobResponse(
        id=job.id,
        url=job.url,
        status=JobStatus(job.status),
        created_at=job.created_at,
        result=result,
        error=job.error,
    )


@router.post(
    "/audit",
    response_model=AuditJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_audit(
    payload: AuditRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> AuditJobResponse:
    """Create a pending audit job and schedule it to run in the background."""
    job = crud.create_job(db, payload.url)
    background_tasks.add_task(
        run_audit_job, job.id, payload.url, payload.check_broken_links
    )
    return _to_response(job)


@router.get("/audit/{job_id}", response_model=AuditJobResponse)
def get_audit(job_id: str, db: Session = Depends(get_db)) -> AuditJobResponse:
    """Fetch the current state (and result, if ready) of an audit job."""
    job = crud.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Audit job not found")
    return _to_response(job)
