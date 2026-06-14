"""Reusable domain logic shared across routers."""
from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import schemas
from .models import Pick, Situation


def options_out(situation: Situation) -> list[schemas.OptionOut]:
    out = [
        schemas.OptionOut(key="a", label=situation.option_a),
        schemas.OptionOut(key="b", label=situation.option_b),
    ]
    if situation.option_c:
        out.append(schemas.OptionOut(key="c", label=situation.option_c))
    return out


def situation_out(situation: Situation) -> schemas.SituationOut:
    return schemas.SituationOut(
        id=situation.id,
        sport=situation.sport,
        game_date=situation.game_date,
        week=situation.week,
        situation_description=situation.situation_description,
        options=options_out(situation),
        daily_date=situation.daily_date,
    )


def community_split(db: Session, situation_id: str) -> schemas.CommunitySplit:
    rows = db.execute(
        select(Pick.choice, func.count(Pick.id))
        .where(Pick.situation_id == situation_id)
        .group_by(Pick.choice)
    ).all()
    counts = {choice: n for choice, n in rows}
    a, b, c = counts.get("a", 0), counts.get("b", 0), counts.get("c", 0)
    return schemas.CommunitySplit(a=a, b=b, c=c, total=a + b + c)


def get_or_assign_daily(db: Session, sport: str, day: date) -> Situation | None:
    """Return the Daily Call for a sport/day, assigning one on demand.

    Demo-friendly rotation: if a situation is already pinned to `day`, use it;
    otherwise pin the oldest unpinned situation; if everything is pinned, fall
    back to a deterministic rotation by day ordinal so there's always a call.
    """
    sport = sport.upper()
    existing = db.scalar(
        select(Situation).where(
            Situation.sport == sport, Situation.daily_date == day
        )
    )
    if existing:
        return existing

    unpinned = db.scalar(
        select(Situation)
        .where(Situation.sport == sport, Situation.daily_date.is_(None))
        .order_by(Situation.created_at)
    )
    if unpinned:
        unpinned.daily_date = day
        db.commit()
        db.refresh(unpinned)
        return unpinned

    pool = db.scalars(
        select(Situation).where(Situation.sport == sport).order_by(Situation.created_at)
    ).all()
    if not pool:
        return None
    return pool[day.toordinal() % len(pool)]


def build_reveal(
    db: Session, situation: Situation, viewer_pick: Pick | None
) -> schemas.RevealOut:
    your_choice = viewer_pick.choice if viewer_pick else None
    return schemas.RevealOut(
        situation_id=situation.id,
        actual_call=situation.actual_call,
        actual_call_label=situation.option_text(situation.actual_call) or "",
        best_call=situation.best_call,
        best_call_label=situation.option_text(situation.best_call) or "",
        outcome=situation.outcome,
        analytics_verdict=situation.analytics_verdict,
        ai_verdict=situation.ai_verdict or situation.analytics_verdict,
        community_split=community_split(db, situation.id),
        your_choice=your_choice,
        you_were_correct=(viewer_pick.correct if viewer_pick else None),
        you_beat_coach=(viewer_pick.beat_coach if viewer_pick else None),
    )
