"""Oaksy data pipeline — pull real NFL 4th-down decisions from nflverse.

Reads free play-by-play data from the nflverse-data GitHub release, finds
high-leverage 4th-down "decision moments," and stores them as Daily-Call
situations in the same database the API uses.

Usage (from the backend/ directory):
    python scripts/pull_nfl.py --season 2023 --limit 40
    python scripts/pull_nfl.py --season 2023 --limit 40 --ai   # also write Claude verdicts

Requires pandas:  pip install -r requirements-pipeline.txt
The "best call" here is a transparent, documented heuristic — swap in a real
EPA/win-probability model for production.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the app package importable when run as a plain script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from app import ai  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models import Situation  # noqa: E402
from app.seed import create_tables  # noqa: E402
from sqlalchemy import select  # noqa: E402

PBP_URL = (
    "https://github.com/nflverse/nflverse-data/releases/download/pbp/"
    "play_by_play_{season}.csv.gz"
)

USE_COLS = [
    "game_id", "home_team", "away_team", "season", "week", "qtr",
    "game_seconds_remaining", "down", "ydstogo", "yardline_100", "play_type",
    "posteam", "defteam", "score_differential", "desc",
    "fourth_down_converted", "touchdown",
]


def _fmt_clock(secs: float) -> str:
    if pd.isna(secs):
        return "late"
    secs = int(secs)
    return f"{secs // 60}:{secs % 60:02d} left in the game"


def _yardline_phrase(yardline_100: float) -> str:
    """yardline_100 = distance to the opponent's end zone."""
    if pd.isna(yardline_100):
        return "midfield"
    y = int(yardline_100)
    if y > 50:
        return f"your own {100 - y}-yard line"
    if y == 50:
        return "midfield"
    return f"the opponent's {y}-yard line"


def _heuristic_best_call(ydstogo: float, yardline_100: float) -> str:
    """Crude, explainable stand-in for an EPA/WP model. Returns 'a'/'b'/'c'."""
    if pd.notna(yardline_100) and yardline_100 <= 38 and ydstogo > 3:
        return "c"  # comfortable field goal
    if pd.notna(ydstogo) and ydstogo <= 2 and pd.notna(yardline_100) and yardline_100 <= 60:
        return "a"  # short yardage, go for it
    if pd.notna(yardline_100) and yardline_100 <= 45 and ydstogo <= 4:
        return "a"
    return "b"  # punt


def _actual_call(play_type: str) -> str | None:
    if play_type in ("run", "pass", "qb_kneel", "qb_spike"):
        return "a"  # went for it
    if play_type == "punt":
        return "b"
    if play_type == "field_goal":
        return "c"
    return None


def build_situations(df: pd.DataFrame, limit: int) -> list[dict]:
    fourth = df[(df["down"] == 4) & df["play_type"].notna()].copy()
    # Focus on interesting, high-leverage spots: 2nd half, one-score games.
    fourth = fourth[
        (fourth["qtr"] >= 3)
        & (fourth["score_differential"].abs() <= 8)
        & (fourth["ydstogo"] <= 6)
    ]
    # Most dramatic first: latest game time.
    fourth = fourth.sort_values("game_seconds_remaining", ascending=True)

    out: list[dict] = []
    for _, p in fourth.iterrows():
        actual = _actual_call(str(p.get("play_type")))
        if actual is None:
            continue

        ydstogo = p.get("ydstogo")
        yardline = p.get("yardline_100")
        diff = p.get("score_differential")
        lead = (
            f"up {int(diff)}" if pd.notna(diff) and diff > 0
            else f"down {abs(int(diff))}" if pd.notna(diff) and diff < 0
            else "tied"
        )
        desc = (
            f"4th-and-{int(ydstogo)} at {_yardline_phrase(yardline)}. "
            f"You're {lead}, {_fmt_clock(p.get('game_seconds_remaining'))}. "
            f"What's the call?"
        )

        best = _heuristic_best_call(ydstogo, yardline)
        converted = bool(p.get("fourth_down_converted") == 1)
        scored = bool(p.get("touchdown") == 1)
        raw = str(p.get("desc") or "").strip()
        outcome = raw[:280] if raw else (
            "Converted the fourth down." if converted else "Did not convert."
        )
        if scored:
            outcome += " (Touchdown on the play.)"

        analytics = {
            "a": "Short yardage in a one-score game — the win-probability math leans toward keeping your offense on the field.",
            "b": "Long yardage outside scoring range — the field-position math favors punting and trusting your defense.",
            "c": "Inside the kicker's range with long yardage — taking the points is the steadier expected-value play.",
        }[best]

        out.append(
            {
                "sport": "NFL",
                "season": int(p.get("season")) if pd.notna(p.get("season")) else None,
                "week": f"Week {int(p.get('week'))}" if pd.notna(p.get("week")) else None,
                "game_id": f"{p.get('game_id')}_4d_{int(p.get('game_seconds_remaining') or 0)}",
                "situation_description": desc,
                "option_a": "Go for it",
                "option_b": "Punt",
                "option_c": "Field goal attempt",
                "actual_call": actual,
                "best_call": best,
                "outcome": outcome,
                "analytics_verdict": analytics,
            }
        )
        if len(out) >= limit:
            break
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Pull NFL 4th-down decisions from nflverse.")
    parser.add_argument("--season", type=int, default=2023)
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--ai", action="store_true", help="Generate Claude verdicts (needs ANTHROPIC_API_KEY)")
    args = parser.parse_args()

    url = PBP_URL.format(season=args.season)
    print(f"Downloading nflverse play-by-play for {args.season} ...")
    df = pd.read_csv(url, compression="gzip", low_memory=False, usecols=lambda c: c in USE_COLS)
    print(f"Loaded {len(df):,} plays. Extracting 4th-down decision moments ...")

    rows = build_situations(df, args.limit)
    print(f"Built {len(rows)} candidate situations.")

    create_tables()
    added = 0
    with SessionLocal() as db:
        for row in rows:
            if db.scalar(select(Situation).where(Situation.game_id == row["game_id"])):
                continue
            s = Situation(
                sport=row["sport"], season=row["season"], week=row["week"],
                game_id=row["game_id"], situation_description=row["situation_description"],
                option_a=row["option_a"], option_b=row["option_b"], option_c=row["option_c"],
                actual_call=row["actual_call"], best_call=row["best_call"],
                outcome=row["outcome"], analytics_verdict=row["analytics_verdict"],
            )
            if args.ai:
                s.ai_verdict = ai.generate_verdict(
                    situation=row["situation_description"],
                    actual_call=s.option_text(row["actual_call"]) or "",
                    best_call=s.option_text(row["best_call"]) or "",
                    outcome=row["outcome"], analytics=row["analytics_verdict"],
                )
            db.add(s)
            added += 1
        db.commit()
    print(f"Done. Added {added} new NFL situation(s) to the database.")


if __name__ == "__main__":
    main()
