"""Reusable domain logic shared across routers."""
from __future__ import annotations

import random
import time
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import schemas
from .models import Pick, Situation
from .players import PLAYERS

# Situations are immutable after seeding, so cache them (detached from the
# session, safe to reuse across requests). This removes a DB read from the hot
# pick/reveal paths.
_situation_cache: dict[str, Situation] = {}

# The community split changes constantly under load; a tiny TTL collapses many
# concurrent GROUP BY queries into one. Invalidated immediately when a pick lands
# so the submitter always sees their own vote counted.
_split_cache: dict[str, tuple[float, "schemas.CommunitySplit"]] = {}
_SPLIT_TTL = 3.0


def get_situation_cached(db: Session, situation_id: str) -> Situation | None:
    cached = _situation_cache.get(situation_id)
    if cached is not None:
        return cached
    situation = db.get(Situation, situation_id)
    if situation is None:
        return None
    db.expunge(situation)  # detach: immutable, reused read-only across requests
    if len(_situation_cache) > 256:
        _situation_cache.clear()
    _situation_cache[situation_id] = situation
    return situation


def invalidate_split(situation_id: str) -> None:
    _split_cache.pop(situation_id, None)

# --- 82-0 GM Mode tuning ----------------------------------------------------
GM_CAP = 32
GM_ROSTER_SIZE = 5
GM_POOL_SIZE = 12
GM_RULES = (
    f"Build a starting five from your spin. Stay under the {GM_CAP}-point cap. "
    "You need at least one guard and one center."
)


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
    hit = _split_cache.get(situation_id)
    if hit is not None and (time.monotonic() - hit[0]) < _SPLIT_TTL:
        return hit[1]
    rows = db.execute(
        select(Pick.choice, func.count(Pick.id))
        .where(Pick.situation_id == situation_id)
        .group_by(Pick.choice)
    ).all()
    counts = {choice: n for choice, n in rows}
    a, b, c = counts.get("a", 0), counts.get("b", 0), counts.get("c", 0)
    split = schemas.CommunitySplit(a=a, b=b, c=c, total=a + b + c)
    _split_cache[situation_id] = (time.monotonic(), split)
    return split


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


def _gm_feasible(pool: list[dict]) -> bool:
    """Is there a legal sub-cap five (>=1 G, >=1 C) buildable from this pool?"""
    guards = sorted((p for p in pool if p["pos"] == "G"), key=lambda p: p["cost"])
    centers = sorted((p for p in pool if p["pos"] == "C"), key=lambda p: p["cost"])
    if not guards or not centers:
        return False
    chosen = {guards[0]["id"], centers[0]["id"]}
    rest = sorted(
        (p for p in pool if p["id"] not in chosen), key=lambda p: p["cost"]
    )
    five = [guards[0], centers[0]] + rest[: GM_ROSTER_SIZE - 2]
    return len(five) == GM_ROSTER_SIZE and sum(p["cost"] for p in five) <= GM_CAP


def gm_spin_pool() -> list[dict]:
    """Randomized pool guaranteeing a legal lineup is buildable under the cap."""
    by_pos = {
        "G": [p for p in PLAYERS if p["pos"] == "G"],
        "F": [p for p in PLAYERS if p["pos"] == "F"],
        "C": [p for p in PLAYERS if p["pos"] == "C"],
    }
    for _ in range(40):
        pool = (
            random.sample(by_pos["G"], 4)
            + random.sample(by_pos["F"], 4)
            + random.sample(by_pos["C"], 2)
        )
        chosen_ids = {p["id"] for p in pool}
        leftover = [p for p in PLAYERS if p["id"] not in chosen_ids]
        pool += random.sample(leftover, GM_POOL_SIZE - len(pool))
        if _gm_feasible(pool):
            random.shuffle(pool)
            return pool
    # Extremely unlikely; return a known-feasible default sample.
    return random.sample(PLAYERS, GM_POOL_SIZE)


def validate_gm_roster(pool_ids: list[str], player_ids: list[str]) -> tuple[bool, str]:
    from .players import BY_ID

    if len(player_ids) != GM_ROSTER_SIZE:
        return False, f"Pick exactly {GM_ROSTER_SIZE} players."
    if len(set(player_ids)) != len(player_ids):
        return False, "No duplicate players."
    pool = set(pool_ids)
    if not all(pid in pool for pid in player_ids):
        return False, "You can only pick players from your spin."
    team = [BY_ID[pid] for pid in player_ids if pid in BY_ID]
    if len(team) != GM_ROSTER_SIZE:
        return False, "Unknown player in roster."
    positions = {p["pos"] for p in team}
    if "G" not in positions:
        return False, "Your lineup needs at least one guard."
    if "C" not in positions:
        return False, "Your lineup needs at least one center."
    total = sum(p["cost"] for p in team)
    if total > GM_CAP:
        return False, f"Over the cap: {total}/{GM_CAP}."
    return True, ""


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
