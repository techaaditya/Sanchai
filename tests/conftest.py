"""Pytest configuration and shared fixtures for Sanchai backend tests.

Provides test isolation by overriding the database path and upload directory
to per-test temporary locations. Without this fixture, tests that use
``TestClient(app)`` would mutate the real development database at
``data/sanchai.db`` because the app's lifespan runs ``init_db()`` and
``seed_all()`` against ``settings.db_path``.

The autouse fixture runs before the per-test ``client`` fixture (autouse fixtures
of the same scope are resolved first), so the lifespan picks up the overridden
paths when the TestClient context manager triggers startup.
"""

from __future__ import annotations

import pytest

from backend.config import settings


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Route database and uploads to a per-test temp directory.

    Each test gets a fresh SQLite file. The app lifespan (``init_db`` +
    ``seed_all``) runs when ``TestClient(app)`` enters its context, so the
    temp database is initialised and seeded automatically before each test
    executes. After the test, ``monkeypatch`` restores the original settings.
    """
    test_db = str(tmp_path / "test_sanchai.db")
    test_uploads = str(tmp_path / "uploads")

    monkeypatch.setattr(settings, "db_path", test_db)
    monkeypatch.setattr(settings, "upload_dir", test_uploads)

    yield tmp_path


@pytest.fixture
def client():
    """Standard FastAPI TestClient with an isolated database."""
    from fastapi.testclient import TestClient
    from backend.main import app

    with TestClient(app) as test_client:
        yield test_client
