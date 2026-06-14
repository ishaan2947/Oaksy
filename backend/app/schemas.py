"""Pydantic request/response schemas."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


# --- Auth -------------------------------------------------------------------
class SignupRequest(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=40)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    display_name: str

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Situations / Daily Call ------------------------------------------------
class OptionOut(BaseModel):
    key: str
    label: str


class SituationOut(BaseModel):
    """The Daily Call card — never leaks the answer before the user picks."""

    id: str
    sport: str
    game_date: date | None
    week: str | None
    situation_description: str
    options: list[OptionOut]
    daily_date: date | None


class CommunitySplit(BaseModel):
    a: int = 0
    b: int = 0
    c: int = 0
    total: int = 0


class RevealOut(BaseModel):
    """Shown after the user picks (or when fetching results)."""

    situation_id: str
    actual_call: str           # option key
    actual_call_label: str
    best_call: str             # option key
    best_call_label: str
    outcome: str
    analytics_verdict: str
    ai_verdict: str
    community_split: CommunitySplit
    your_choice: str | None = None
    you_were_correct: bool | None = None
    you_beat_coach: bool | None = None


# --- Picks ------------------------------------------------------------------
class PickRequest(BaseModel):
    situation_id: str
    choice: str = Field(pattern="^[abc]$")
    reasoning: str | None = Field(default=None, max_length=600)
    anon_id: str | None = None  # used when not logged in


# --- Coach Score ------------------------------------------------------------
class CoachScore(BaseModel):
    display_name: str
    total_calls: int
    correct_calls: int
    win_rate: float            # 0-100, vs the analytics-optimal call
    beat_coach_count: int
    debate_wins: int
    rank_label: str
    gm_teams: int = 0
    gm_rating: float = 0.0     # 0-100 average Claude team score
    gm_rank_label: str = "Unrated"


class LeaderboardEntry(BaseModel):
    display_name: str
    win_rate: float
    total_calls: int


# --- Debate Arena -----------------------------------------------------------
class DebatePostOut(BaseModel):
    pick_id: str
    author: str
    choice: str
    choice_label: str
    reasoning: str
    votes: int
    you_voted: bool = False


class DebateSituationOut(BaseModel):
    situation_id: str
    sport: str
    situation_description: str
    options: list[OptionOut]
    best_call: str
    best_call_label: str
    community_split: CommunitySplit
    posts: list[DebatePostOut]


class DebateArenaOut(BaseModel):
    week_label: str
    situations: list[DebateSituationOut]


# --- 82-0 GM Mode -----------------------------------------------------------
class PlayerOut(BaseModel):
    id: str
    name: str
    pos: str        # G | F | C
    era: str
    cost: int
    tag: str


class SpinOut(BaseModel):
    spin_id: str
    cap: int
    roster_size: int
    rules: str
    pool: list[PlayerOut]


class GMSubmitRequest(BaseModel):
    spin_id: str
    player_ids: list[str] = Field(min_length=1, max_length=8)
    anon_id: str | None = None


class GMResultOut(BaseModel):
    team: list[PlayerOut]
    total_cost: int
    cap: int
    score: int
    verdict: str
    share_line: str
