"""Coach Score (identity layer) and the weekly leaderboard."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..deps import get_current_user
from ..models import DebateVote, GMTeam, Pick, Situation, User

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


def _streaks(pick_dates: list[date], today: date | None = None) -> tuple[int, int]:
    """Return (current, longest) run of consecutive days from a list of dates.

    `today` is injectable for testing; it defaults to the UTC date so it matches
    how `created_at` is stored (the "played today" check stays consistent)."""
    days = sorted(set(pick_dates))
    if not days:
        return 0, 0

    longest = run = 1
    for prev, cur in zip(days, days[1:]):
        run = run + 1 if cur - prev == timedelta(days=1) else 1
        longest = max(longest, run)

    # Current streak counts back from the most recent day, but only "alive" if the
    # last play was today or yesterday (a full missed day breaks it).
    if today is None:
        today = datetime.now(timezone.utc).date()
    if days[-1] not in (today, today - timedelta(days=1)):
        return 0, longest
    current = 1
    for prev, cur in zip(reversed(days), reversed(days[:-1])):
        if prev - cur == timedelta(days=1):
            current += 1
        else:
            break
    return current, longest


def _sharp_label(score: float, graded: int) -> str:
    if graded < 3:
        return "Unrated"
    if score >= 72:
        return "Sharp"
    if score >= 56:
        return "Calibrated"
    if score >= 44:
        return "Even"
    if score >= 30:
        return "Loose"
    return "Overconfident"


def _sharp_score(db: Session, user: User) -> tuple[float, str]:
    """Calibration score from confidence-weighted picks. Confident + right pushes
    it up; confident + wrong pulls it down. 50 = neutral, no info."""
    rows = db.execute(
        select(Pick.confidence, Pick.correct).where(
            Pick.user_id == user.id, Pick.confidence.is_not(None)
        )
    ).all()
    if not rows:
        return 50.0, "Unrated"
    # Each graded pick scores in [-3, +3]; average mapped onto 0-100.
    pts = sum((c if correct else -c) for c, correct in rows)
    avg = pts / len(rows)
    score = round((avg + 3) / 6 * 100, 1)
    return score, _sharp_label(score, len(rows))


def _survivor(correct_flags: list[bool]) -> tuple[int, int]:
    """(current, best) run of consecutive correct calls. Current is the trailing
    run from the most recent pick — one miss resets it (the loss-aversion hook)."""
    best = run = 0
    for c in correct_flags:
        run = run + 1 if c else 0
        best = max(best, run)
    current = 0
    for c in reversed(correct_flags):
        if c:
            current += 1
        else:
            break
    return current, best


def _badges(m: dict) -> list[schemas.BadgeOut]:
    """Achievement badges derived from the user's record. (id, label, desc, test)."""
    defs = [
        ("first_call", "First Call", "Make your first Daily Call", m["total"] >= 1),
        ("regular", "Regular", "Make 10 calls", m["total"] >= 10),
        ("centurion", "Centurion", "Make 100 calls", m["total"] >= 100),
        ("coach_killer", "Coach Killer", "Beat the coach once", m["beat"] >= 1),
        ("out_coacher", "Out-Coacher", "Beat the coach 10 times", m["beat"] >= 10),
        ("on_a_roll", "On a Roll", "Hit a 3-day streak", m["longest_streak"] >= 3),
        ("habit", "Habit Formed", "Hit a 7-day streak", m["longest_streak"] >= 7),
        ("survivor", "Survivor", "Get 5 calls right in a row", m["survivor_best"] >= 5),
        ("untouchable", "Untouchable", "Get 10 calls right in a row", m["survivor_best"] >= 10),
        ("sharp", "Sharp Shooter", "Reach a Sharp Score of 80", m["sharp_score"] >= 80 and m["graded"] >= 3),
        ("three_sport", "Three-Sport Coach", "Make a call in NFL, NBA, and MLB", m["sports"] >= 3),
        ("architect", "Roster Architect", "Build an 82-0 team", m["gm_teams"] >= 1),
        ("crowd_favorite", "Crowd Favorite", "Win a debate upvote", m["debate_wins"] >= 1),
    ]
    return [
        schemas.BadgeOut(id=i, label=l, description=d, earned=bool(t))
        for (i, l, d, t) in defs
    ]


def _gm_rank_label(rating: float, teams: int) -> str:
    if teams == 0:
        return "Unrated"
    if rating >= 90:
        return "Hall of Fame"
    if rating >= 80:
        return "Elite"
    if rating >= 70:
        return "Contender"
    if rating >= 60:
        return "Playoff"
    return "Lottery"


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

    # GM Mode: number of teams built + average Claude rating.
    gm_teams = (
        db.scalar(select(func.count(GMTeam.id)).where(GMTeam.user_id == user.id)) or 0
    )
    gm_avg = (
        db.scalar(select(func.avg(GMTeam.score)).where(GMTeam.user_id == user.id)) or 0
    )
    gm_rating = round(float(gm_avg), 1)

    # Streak: distinct days the user made a Daily Call.
    pick_dts = db.scalars(
        select(Pick.created_at).where(Pick.user_id == user.id)
    ).all()
    current_streak, longest_streak = _streaks([dt.date() for dt in pick_dts if dt])

    # Survivor: consecutive correct calls, in chronological order.
    correct_flags = [
        bool(c)
        for c in db.scalars(
            select(Pick.correct).where(Pick.user_id == user.id).order_by(Pick.created_at)
        ).all()
    ]
    survivor_current, survivor_best = _survivor(correct_flags)

    # Distinct sports played (for the Three-Sport Coach badge).
    sport_count = (
        db.scalar(
            select(func.count(func.distinct(Situation.sport)))
            .select_from(Pick)
            .join(Situation, Pick.situation_id == Situation.id)
            .where(Pick.user_id == user.id)
        )
        or 0
    )

    sharp_score, sharp_label = _sharp_score(db, user)
    graded = db.scalar(
        select(func.count(Pick.id)).where(
            Pick.user_id == user.id, Pick.confidence.is_not(None)
        )
    ) or 0

    badges = _badges(
        {
            "total": total,
            "beat": beat,
            "longest_streak": longest_streak,
            "survivor_best": survivor_best,
            "sharp_score": sharp_score,
            "graded": graded,
            "sports": sport_count,
            "gm_teams": gm_teams,
            "debate_wins": debate_wins,
        }
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
        current_streak=current_streak,
        longest_streak=longest_streak,
        survivor_current=survivor_current,
        survivor_best=survivor_best,
        sharp_score=sharp_score,
        sharp_label=sharp_label,
        badges=badges,
        reminders=user.reminders is not False,
        gm_teams=gm_teams,
        gm_rating=gm_rating,
        gm_rank_label=_gm_rank_label(gm_rating, gm_teams),
    )


@router.get("/me/score", response_model=schemas.CoachScore)
def my_score(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _coach_score(db, user)


@router.put("/me/reminders")
def set_reminders(
    payload: schemas.ReminderPref,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user.reminders = payload.enabled
    db.commit()
    return {"reminders": payload.enabled}


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
