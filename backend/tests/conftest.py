"""Shared test fixtures: a SQLite-backed app client and session factory.

Postgres isn't required for tests. We spin up an in-memory SQLite database
shared across connections (StaticPool), create the schema from the ORM
metadata, override the request-time get_db dependency, and point the background
worker's SessionLocal at the same database so jobs are visible end to end.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import worker
from app.db import models  # noqa: F401 - register tables on Base.metadata
from app.db.session import Base, get_db
from app.main import app


@pytest.fixture
def test_sessionmaker():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    try:
        yield SessionLocal
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(test_sessionmaker, monkeypatch):
    def _override_get_db():
        db = test_sessionmaker()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    # The background worker opens its own session; point it at the test DB too.
    monkeypatch.setattr(worker, "SessionLocal", test_sessionmaker)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
