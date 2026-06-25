"""Pydantic request/response schemas."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Auth -------------------------------------------------------------------
class SignupRequest(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=40)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    display_name: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Situations / Daily Call ------------------------------------------------
class OptionOut(BaseModel):
    key: str
    label: str


class GameState(BaseModel):
    """Visual game-state for the scenario diagram. All optional so situations
    without curated state still render a plain field/court."""

    clock: str | None = None        # e.g. "4th · 3:50", "OT", "2nd · 0:38"
    your_score: int | None = None
    opp_score: int | None = None
    tag: str | None = None          # situational chip: "4th & 2", "Up 3", "Inbound"
    ball_on: int | None = None      # 0..100 toward the opponent's goal (NFL)
    poss: str | None = None         # "you" | "them" | "kick"
    zone: str | None = None         # ball location label (NBA): top|wing|inbound|post
    bases: list[int] | None = None  # [1B, 2B, 3B] occupied (MLB, v2)
    outs: int | None = None         # MLB, v2


class SituationOut(BaseModel):
    """The Daily Call card — never leaks the answer before the user picks."""

    id: str
    sport: str
    game_date: date | None
    week: str | None
    situation_description: str
    options: list[OptionOut]
    daily_date: date | None
    game_state: GameState | None = None


class CommunitySplit(BaseModel):
    a: int = 0
    b: int = 0
    c: int = 0
    d: int = 0
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
    # Win probability per option key ("a"/"b"/"c") from the model, independent of
    # how this one game ended. Absent for situations without curated odds.
    win_probabilities: dict[str, int] | None = None
    your_choice: str | None = None
    you_were_correct: bool | None = None
    you_beat_coach: bool | None = None


# --- Picks ------------------------------------------------------------------
class PickRequest(BaseModel):
    situation_id: str
    choice: str = Field(pattern="^[abcd]$")
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
    current_streak: int = 0    # consecutive days with a Daily Call
    longest_streak: int = 0
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


# --- Waitlist ---------------------------------------------------------------
class WaitlistRequest(BaseModel):
    email: EmailStr
    source: str | None = Field(default=None, max_length=60)


class WaitlistOut(BaseModel):
    ok: bool
    already: bool
    count: int


class WaitlistCount(BaseModel):
    count: int


# --- Feedback poll ----------------------------------------------------------
class FeedbackRequest(BaseModel):
    rating: str = Field(pattern="^(yes|maybe|no)$")
    comment: str | None = Field(default=None, max_length=1000)
    anon_id: str | None = None
    source: str | None = Field(default=None, max_length=60)


class FeedbackSummary(BaseModel):
    yes: int = 0
    maybe: int = 0
    no: int = 0
    total: int = 0
