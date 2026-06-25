"""The Debate Arena — the weekly social loop.

The most-debated Daily Calls of the recent window get surfaced, and the
community votes on whose *reasoning* was best. Reasonings are simply picks that
included a written argument; votes are upvotes on those picks.
"""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import schemas, services
from ..database import get_db
from ..deps import get_current_user, get_optional_user
from ..models import DebateVote, Pick, Situation, User
from ..seed_data import MATCHUPS

router = APIRouter(prefix="/api/debate", tags=["debate"])

# How many days back counts as "this week's" most-debated calls, and how many
# situations / reasonings to surface.
_WINDOW_DAYS = 7
_MAX_SITUATIONS = 4
_MAX_POSTS = 12


def _week_label(today: date) -> str:
    year, week, _ = today.isocalendar()
    return f"Week {week}, {year}"


@router.get("/current", response_model=schemas.DebateArenaOut)
def current_arena(
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    today = date.today()
    since = today - timedelta(days=_WINDOW_DAYS)

    # Most-debated situations: featured in the window, ranked by pick volume.
    ranked = db.execute(
        select(Situation.id, func.count(Pick.id).label("n"))
        .join(Pick, Pick.situation_id == Situation.id)
        .where(Situation.daily_date.is_not(None), Situation.daily_date >= since)
        .group_by(Situation.id)
        .order_by(func.count(Pick.id).desc())
        .limit(_MAX_SITUATIONS)
    ).all()
    situation_ids = [row[0] for row in ranked]

    # Fallback for fresh installs: any situation that has reasoning attached.
    if not situation_ids:
        situation_ids = [
            row[0]
            for row in db.execute(
                select(Pick.situation_id, func.count(Pick.id))
                .where(Pick.reasoning.is_not(None))
                .group_by(Pick.situation_id)
                .order_by(func.count(Pick.id).desc())
                .limit(_MAX_SITUATIONS)
            ).all()
        ]

    voted_pick_ids: set[str] = set()
    if user:
        voted_pick_ids = {
            r[0]
            for r in db.execute(
                select(DebateVote.pick_id).where(DebateVote.user_id == user.id)
            ).all()
        }

    out_situations: list[schemas.DebateSituationOut] = []
    for sid in situation_ids:
        situation = db.get(Situation, sid)
        if not situation:
            continue
        posts = _posts_for_situation(db, sid, voted_pick_ids)
        out_situations.append(
            schemas.DebateSituationOut(
                situation_id=situation.id,
                sport=situation.sport,
                situation_description=situation.situation_description,
                matchup=MATCHUPS.get(situation.game_id),
                options=services.options_out(situation),
                best_call=situation.best_call,
                best_call_label=situation.option_text(situation.best_call) or "",
                community_split=services.community_split(db, situation.id),
                posts=posts,
            )
        )

    return schemas.DebateArenaOut(
        week_label=_week_label(today), situations=out_situations
    )


def _posts_for_situation(
    db: Session, situation_id: str, voted_pick_ids: set[str]
) -> list[schemas.DebatePostOut]:
    picks = db.scalars(
        select(Pick)
        .where(Pick.situation_id == situation_id, Pick.reasoning.is_not(None))
        .limit(50)
    ).all()
    situation = db.get(Situation, situation_id)
    posts: list[schemas.DebatePostOut] = []
    for p in picks:
        vote_count = (
            db.scalar(select(func.count(DebateVote.id)).where(DebateVote.pick_id == p.id))
            or 0
        )
        posts.append(
            schemas.DebatePostOut(
                pick_id=p.id,
                author=p.user.display_name if p.user else "Anonymous",
                choice=p.choice,
                choice_label=situation.option_text(p.choice) or "" if situation else "",
                reasoning=p.reasoning or "",
                votes=vote_count,
                you_voted=p.id in voted_pick_ids,
            )
        )
    posts.sort(key=lambda x: x.votes, reverse=True)
    return posts[:_MAX_POSTS]


@router.post("/posts/{pick_id}/vote", status_code=201)
def vote(
    pick_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    pick = db.get(Pick, pick_id)
    if not pick or not pick.reasoning:
        raise HTTPException(404, "Reasoning not found")
    if pick.user_id == user.id:
        raise HTTPException(400, "You can't vote for your own reasoning")

    existing = db.scalar(
        select(DebateVote).where(
            DebateVote.pick_id == pick_id, DebateVote.user_id == user.id
        )
    )
    if existing:  # toggle off
        db.delete(existing)
        db.commit()
        voted = False
    else:
        db.add(DebateVote(pick_id=pick_id, user_id=user.id))
        db.commit()
        voted = True

    votes = db.scalar(
        select(func.count(DebateVote.id)).where(DebateVote.pick_id == pick_id)
    ) or 0
    return {"pick_id": pick_id, "you_voted": voted, "votes": votes}


@router.post("/{situation_id}/argue", status_code=201)
def argue(
    situation_id: str,
    payload: schemas.ArgueRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Post (or update) your argument on a situation, straight from the Debate
    Arena. If you've already made this call, we keep your pick and just attach
    your reasoning; otherwise we record your call with it."""
    situation = db.get(Situation, situation_id)
    if not situation:
        raise HTTPException(404, "Situation not found")
    if not situation.option_text(payload.choice):
        raise HTTPException(400, "That option isn't available on this situation")

    pick = db.scalar(
        select(Pick).where(
            Pick.situation_id == situation_id, Pick.user_id == user.id
        )
    )
    if pick:
        # Keep their original call (it counts toward their score); add the argument.
        pick.reasoning = payload.reasoning.strip()
    else:
        correct = payload.choice == situation.best_call
        pick = Pick(
            situation_id=situation_id,
            user_id=user.id,
            choice=payload.choice,
            reasoning=payload.reasoning.strip(),
            correct=correct,
            beat_coach=correct and situation.actual_call != situation.best_call,
        )
        db.add(pick)
    db.commit()
    services.invalidate_split(situation_id)
    return {"ok": True, "pick_id": pick.id}
