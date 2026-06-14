"""Coach Score (identity layer) and the weekly leaderboard."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..deps import get_current_user
from ..models import DebateVote, Pick, User

router = APIRouter(prefix="/api/users", tags=["users"])


def _rank_label(win_rate: float, total: int) -> str:
    if total < 3:
        return "Rookie"
    if win_rate >= 75:
        return "Elite"
    if win_rate >= 60:
        return "All-Pro"
    if win_rate >= 45:
        return "Starter"
    return "Benchwarmer"


def _coach_score(db: Session, user: User) -> schemas.CoachScore:
    total = db.scalar(select(func.count(Pick.id)).where(Pick.user_id == user.id)) or 0
    correct = (
        db.scalar(
            select(func.count(Pick.id)).where(
                Pick.user_id == user.id, Pick.correct.is_(True)
            )
        )
        or 0
    )
    beat = (
        db.scalar(
            select(func.count(Pick.id)).where(
                Pick.user_id == user.id, Pick.beat_coach.is_(True)
            )
        )
        or 0
    )
    # Debate wins: votes received across all of this user's reasonings.
    debate_wins = (
        db.scalar(
            select(func.count(DebateVote.id))
            .join(Pick, DebateVote.pick_id == Pick.id)
            .where(Pick.user_id == user.id)
        )
        or 0
    )

    win_rate = round((correct / total) * 100, 1) if total else 0.0
    return schemas.CoachScore(
        display_name=user.display_name,
        total_calls=total,
        correct_calls=correct,
        win_rate=win_rate,
        beat_coach_count=beat,
        debate_wins=debate_wins,
        rank_label=_rank_label(win_rate, total),
    )


@router.get("/me/score", response_model=schemas.CoachScore)
def my_score(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _coach_score(db, user)


@router.get("/leaderboard", response_model=list[schemas.LeaderboardEntry])
def leaderboard(limit: int = Query(default=20, le=100), db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            User.display_name,
            func.count(Pick.id),
            func.sum(case((Pick.correct.is_(True), 1), else_=0)),
        )
        .join(Pick, Pick.user_id == User.id)
        .group_by(User.id)
        .having(func.count(Pick.id) > 0)
    ).all()

    entries = [
        schemas.LeaderboardEntry(
            display_name=name,
            total_calls=total,
            win_rate=round(((correct or 0) / total) * 100, 1) if total else 0.0,
        )
        for name, total, correct in rows
    ]
    entries.sort(key=lambda e: (e.win_rate, e.total_calls), reverse=True)
    return entries[:limit]
