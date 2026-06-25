"""Database models for Oaksy.

Core objects:
  * Situation  — one real game decision moment (the Daily Call).
  * User       — an account (email/password).
  * Pick       — a user's (or anonymous) call on a situation.
  * DebateVote — an upvote on a pick's reasoning in the weekly Debate Arena.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Situation(Base):
    """A single real, post-game decision moment fans react to."""

    __tablename__ = "situations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    sport: Mapped[str] = mapped_column(String, index=True)  # "NFL" | "NBA"
    season: Mapped[int | None] = mapped_column(Integer, nullable=True)
    week: Mapped[str | None] = mapped_column(String, nullable=True)
    game_id: Mapped[str | None] = mapped_column(String, nullable=True)
    game_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    situation_description: Mapped[str] = mapped_column(Text)

    option_a: Mapped[str] = mapped_column(String)
    option_b: Mapped[str] = mapped_column(String)
    option_c: Mapped[str | None] = mapped_column(String, nullable=True)

    # Option keys: "a" | "b" | "c"
    actual_call: Mapped[str] = mapped_column(String)  # what the real coach did
    best_call: Mapped[str] = mapped_column(String)    # what the data favored

    outcome: Mapped[str] = mapped_column(Text)
    analytics_verdict: Mapped[str] = mapped_column(Text)
    ai_verdict: Mapped[str | None] = mapped_column(Text, nullable=True)

    # The day this situation is featured as the Daily Call (one per sport per day).
    daily_date: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    picks: Mapped[list["Pick"]] = relationship(
        back_populates="situation", cascade="all, delete-orphan"
    )

    def options(self) -> dict[str, str | None]:
        return {"a": self.option_a, "b": self.option_b, "c": self.option_c}

    def option_text(self, key: str | None) -> str | None:
        if key is None:
            return None
        return self.options().get(key)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    picks: Mapped[list["Pick"]] = relationship(back_populates="user")


class Pick(Base):
    """A call made on a situation. user_id OR anon_id identifies the caller."""

    __tablename__ = "picks"
    __table_args__ = (
        UniqueConstraint("situation_id", "user_id", name="uq_pick_user"),
        UniqueConstraint("situation_id", "anon_id", name="uq_pick_anon"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    situation_id: Mapped[str] = mapped_column(
        ForeignKey("situations.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=True
    )
    anon_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)

    choice: Mapped[str] = mapped_column(String)  # "a" | "b" | "c"
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Computed at submit time against the situation.
    correct: Mapped[bool] = mapped_column(Boolean, default=False)      # picked the data-optimal call
    beat_coach: Mapped[bool] = mapped_column(Boolean, default=False)   # optimal AND coach didn't

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    situation: Mapped["Situation"] = relationship(back_populates="picks")
    user: Mapped["User | None"] = relationship(back_populates="picks")
    votes: Mapped[list["DebateVote"]] = relationship(
        back_populates="pick", cascade="all, delete-orphan"
    )


class GMSpin(Base):
    """A wheel spin in 82-0 GM Mode — the randomized pool you build from."""

    __tablename__ = "gm_spins"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    anon_id: Mapped[str | None] = mapped_column(String, nullable=True)
    player_ids: Mapped[list[str]] = mapped_column(JSON)  # the pool
    cap: Mapped[int] = mapped_column(Integer)
    roster_size: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class GMTeam(Base):
    """A submitted 82-0 roster and its Claude verdict."""

    __tablename__ = "gm_teams"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    spin_id: Mapped[str] = mapped_column(ForeignKey("gm_spins.id"))
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    anon_id: Mapped[str | None] = mapped_column(String, nullable=True)
    player_ids: Mapped[list[str]] = mapped_column(JSON)
    total_cost: Mapped[int] = mapped_column(Integer)
    score: Mapped[int] = mapped_column(Integer)  # 0-100
    verdict: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class FeedbackEntry(Base):
    """A quick in-app feedback poll response from a tester."""

    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    rating: Mapped[str] = mapped_column(String)  # "yes" | "maybe" | "no"
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    anon_id: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class WaitlistEntry(Base):
    """A pre-launch / mobile-beta email signup from the landing page."""

    __tablename__ = "waitlist"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DebateVote(Base):
    """An upvote on a pick's reasoning in the weekly Debate Arena."""

    __tablename__ = "debate_votes"
    __table_args__ = (UniqueConstraint("pick_id", "user_id", name="uq_vote"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    pick_id: Mapped[str] = mapped_column(
        ForeignKey("picks.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    pick: Mapped["Pick"] = relationship(back_populates="votes")
