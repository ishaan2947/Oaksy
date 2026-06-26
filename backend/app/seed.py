"""Idempotent database seeding: tables + curated situations + AI verdicts.

Run directly:  python -m app.seed
Also invoked automatically on app startup so a fresh clone has content.
"""
from __future__ import annotations

import logging

from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError

from . import ai
from .database import Base, SessionLocal, engine
from .models import Situation
from .seed_data import SEED_SITUATIONS

logger = logging.getLogger("oaksy.seed")

# Columns added after the first deploy. There's no Alembic in this project, so we
# apply these forward-only "ADD COLUMN"s by hand on startup. ADD COLUMN of a
# nullable column is instant + safe + idempotent on both SQLite and Postgres.
_ADDED_COLUMNS: dict[str, list[tuple[str, str]]] = {
    "situations": [("option_d", "ALTER TABLE situations ADD COLUMN option_d VARCHAR")],
    "picks": [("confidence", "ALTER TABLE picks ADD COLUMN confidence INTEGER")],
    "users": [("reminders", "ALTER TABLE users ADD COLUMN reminders BOOLEAN")],
}


def _ensure_columns() -> None:
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    for table, cols in _ADDED_COLUMNS.items():
        if table not in tables:
            continue  # fresh DB — create_all already made it with every column
        existing = {c["name"] for c in insp.get_columns(table)}
        for col, ddl in cols:
            if col not in existing:
                with engine.begin() as conn:
                    conn.execute(text(ddl))
                logger.info("Added missing column %s.%s", table, col)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_columns()


def _apply_curated(situation: Situation, row: dict) -> None:
    """Copy curated, non-AI fields from a seed row onto a Situation."""
    situation.sport = row["sport"]
    situation.season = row.get("season")
    situation.week = row.get("week")
    situation.situation_description = row["situation_description"]
    situation.option_a = row["option_a"]
    situation.option_b = row["option_b"]
    situation.option_c = row.get("option_c")
    situation.option_d = row.get("option_d")
    situation.actual_call = row["actual_call"]
    situation.best_call = row["best_call"]
    situation.outcome = row["outcome"]
    situation.analytics_verdict = row["analytics_verdict"]


def _verdict_for(situation: Situation, row: dict) -> str:
    return ai.generate_verdict(
        situation=row["situation_description"],
        actual_call=situation.option_text(row["actual_call"]) or "",
        best_call=situation.option_text(row["best_call"]) or "",
        outcome=row["outcome"],
        analytics=row["analytics_verdict"],
    )


def seed_situations(generate_ai: bool = True) -> int:
    """Upsert curated situations. Inserts new ones (returns count added) and
    refreshes curated fields on existing ones so content edits reach prod. The
    AI verdict is only generated when missing, so re-seeds cost no API calls."""
    added = 0
    with SessionLocal() as db:
        for row in SEED_SITUATIONS:
            existing = db.scalar(
                select(Situation).where(Situation.game_id == row["game_id"])
            )
            if existing:
                _apply_curated(existing, row)
                if generate_ai and not existing.ai_verdict:
                    existing.ai_verdict = _verdict_for(existing, row)
                try:
                    db.commit()  # no-op UPDATE emitted only if a field changed
                except IntegrityError:
                    db.rollback()
                continue

            situation = Situation(game_id=row["game_id"])
            _apply_curated(situation, row)
            if generate_ai:
                situation.ai_verdict = _verdict_for(situation, row)
            db.add(situation)
            try:
                db.commit()  # commit per row so a race (multi-worker boot) is safe
                added += 1
            except IntegrityError:
                db.rollback()  # another worker inserted this one first — fine
    return added


def run() -> None:
    create_tables()
    added = seed_situations()
    logger.info("Seed complete: %d new situation(s) added.", added)
    print(f"Seed complete: {added} new situation(s) added.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
