"""Background worker that runs an audit and records its terminal state.

Runs after the HTTP response is sent (via FastAPI BackgroundTasks), so it opens
its own database session rather than reusing the request's. The whole body is
wrapped so the job always ends in a terminal state ("done" or "failed") and the
worker never crashes silently.
"""

from app.audit.engine import run_audit
from app.db.crud import update_job_status
from app.db.session import SessionLocal


async def run_audit_job(job_id: str, url: str, check_broken_links: bool) -> None:
    """Run the audit for ``job_id`` and persist the result (or the failure)."""
    db = SessionLocal()
    try:
        update_job_status(db, job_id, "running")
        result = await run_audit(url, check_broken_links=check_broken_links)
        update_job_status(db, job_id, "done", result_json=result.model_dump(mode="json"))
    except Exception as exc:  # noqa: BLE001 - always record a terminal state
        try:
            update_job_status(db, job_id, "failed", error=str(exc))
        except Exception:  # noqa: BLE001 - last-resort guard; nothing else we can do
            pass
    finally:
        db.close()
