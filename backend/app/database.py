"""SQLAlchemy engine + session. SQLite by default, Postgres via DATABASE_URL."""
from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings


def _normalize_url(url: str) -> str:
    """Hosts (Render/Heroku) hand out postgres:// URLs that SQLAlchemy maps to
    psycopg2. Rewrite to the psycopg (v3) driver we actually ship."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


DATABASE_URL = _normalize_url(settings.database_url)
_is_sqlite = DATABASE_URL.startswith("sqlite")

# SQLite needs check_same_thread disabled for FastAPI's threaded request model.
connect_args = {"check_same_thread": False} if _is_sqlite else {}

# Production (Postgres) pooling: pre_ping drops dead connections (Render recycles
# them), recycle avoids stale ones, and a healthy pool absorbs concurrent load.
engine_kwargs: dict = {"connect_args": connect_args, "future": True, "pool_pre_ping": True}
if not _is_sqlite:
    engine_kwargs.update(pool_size=10, max_overflow=20, pool_recycle=300)

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    """FastAPI dependency — yields a request-scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
