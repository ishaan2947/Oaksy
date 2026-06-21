"""Pytest fixtures: an isolated, freshly-seeded app instance with AI forced off.

Env is set BEFORE importing the app so config (cached at import) picks up the
throwaway SQLite DB and the empty API key (deterministic fallback verdicts).
"""
import os
import tempfile
import uuid
from pathlib import Path

_DB = Path(tempfile.gettempdir()) / f"oaksy_test_{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_DB.as_posix()}"
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    # `with` triggers the lifespan (create tables + seed situations).
    with TestClient(app) as c:
        yield c
    try:
        _DB.unlink()
    except OSError:
        pass


@pytest.fixture
def make_user(client):
    """Return a factory creating a fresh user; yields (headers, email)."""
    def _make(name="Coach"):
        email = f"{uuid.uuid4().hex[:10]}@oaksy.app"
        res = client.post(
            "/api/auth/signup",
            json={"email": email, "display_name": name, "password": "password123"},
        )
        assert res.status_code == 201, res.text
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}, email

    return _make


@pytest.fixture
def daily(client):
    """Today's NFL Daily Call (answer hidden)."""
    return client.get("/api/situations/daily?sport=NFL").json()
