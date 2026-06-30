"""Tests for the audit API endpoints and background worker.

run_audit is monkeypatched throughout — these tests never hit the network.
"""

from datetime import datetime, timezone

import pytest

from app.api import worker
from app.db import crud
from app.models.schemas import AuditResult


async def _fake_run_audit(url: str, check_broken_links: bool = False) -> AuditResult:
    return AuditResult(
        url=url,
        final_url=url,
        status_code=200,
        fetched_at=datetime.now(timezone.utc),
        overall_score=88,
        category_scores=[],
        checks=[],
    )


async def _boom_run_audit(url: str, check_broken_links: bool = False) -> AuditResult:
    raise RuntimeError("kaboom")


# ---- POST /api/audit ------------------------------------------------------


def test_post_audit_returns_202_pending(client, monkeypatch):
    # Background task runs after the response; stub run_audit so it's offline.
    monkeypatch.setattr(worker, "run_audit", _fake_run_audit)

    response = client.post("/api/audit", json={"url": "https://example.com"})

    assert response.status_code == 202
    body = response.json()
    assert body["id"]
    assert body["url"] == "https://example.com"
    assert body["status"] == "pending"
    assert body["result"] is None
    assert body["error"] is None


def test_post_audit_trims_url_and_rejects_empty(client, monkeypatch):
    monkeypatch.setattr(worker, "run_audit", _fake_run_audit)

    ok = client.post("/api/audit", json={"url": "  https://example.com  "})
    assert ok.status_code == 202
    assert ok.json()["url"] == "https://example.com"

    bad = client.post("/api/audit", json={"url": "   "})
    assert bad.status_code == 422  # validation error


def test_post_then_get_reaches_done(client, monkeypatch):
    # TestClient runs the background task synchronously after the response,
    # so by the time we GET, the job has completed.
    monkeypatch.setattr(worker, "run_audit", _fake_run_audit)

    job_id = client.post("/api/audit", json={"url": "https://example.com"}).json()["id"]

    got = client.get(f"/api/audit/{job_id}")
    assert got.status_code == 200
    body = got.json()
    assert body["status"] == "done"
    assert body["result"] is not None
    assert body["result"]["overall_score"] == 88


# ---- GET /api/audit/{job_id} ----------------------------------------------


def test_get_unknown_job_returns_404(client):
    response = client.get("/api/audit/does-not-exist")
    assert response.status_code == 404


# ---- Worker directly ------------------------------------------------------


@pytest.mark.asyncio
async def test_worker_marks_job_done(client, test_sessionmaker, monkeypatch):
    monkeypatch.setattr(worker, "run_audit", _fake_run_audit)

    db = test_sessionmaker()
    job = crud.create_job(db, "https://example.com")
    job_id = job.id
    db.close()

    await worker.run_audit_job(job_id, "https://example.com", False)

    body = client.get(f"/api/audit/{job_id}").json()
    assert body["status"] == "done"
    assert body["result"]["overall_score"] == 88


@pytest.mark.asyncio
async def test_worker_records_failure(client, test_sessionmaker, monkeypatch):
    monkeypatch.setattr(worker, "run_audit", _boom_run_audit)

    db = test_sessionmaker()
    job = crud.create_job(db, "https://example.com")
    job_id = job.id
    db.close()

    await worker.run_audit_job(job_id, "https://example.com", False)

    body = client.get(f"/api/audit/{job_id}").json()
    assert body["status"] == "failed"
    assert "kaboom" in body["error"]
    assert body["result"] is None


def test_health_still_works(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
