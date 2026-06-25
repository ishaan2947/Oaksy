"""Idempotent database seeding: tables + curated situations + AI verdicts.

Run directly:  python -m app.seed
Also invoked automatically on app startup so a fresh clone has content.
"""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from . import ai
from .database import Base, SessionLocal, engine
from .models import Situation
from .seed_data import SEED_SITUATIONS

logger = logging.getLogger("oaksy.seed")


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_situations(generate_ai: bool = True) -> int:
    """Insert any curated situations not already present. Returns count added."""
    added = 0
    with SessionLocal() as db:
        for row in SEED_SITUATIONS:
            exists = db.scalar(
                select(Situation).where(Situation.game_id == row["game_id"])
            )
            if exists:
                continue

            situation = Situation(
                sport=row["sport"],
                season=row.get("season"),
                week=row.get("week"),
                game_id=row["game_id"],
                situation_description=row["situation_description"],
                option_a=row["option_a"],
                option_b=row["option_b"],
                option_c=row.get("option_c"),
                actual_call=row["actual_call"],
                best_call=row["best_call"],
                outcome=row["outcome"],
                analytics_verdict=row["analytics_verdict"],
            )

            if generate_ai:
                situation.ai_verdict = ai.generate_verdict(
                    situation=row["situation_description"],
                    actual_call=situation.option_text(row["actual_call"]) or "",
                    best_call=situation.option_text(row["best_call"]) or "",
                    outcome=row["outcome"],
                    analytics=row["analytics_verdict"],
                )
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
