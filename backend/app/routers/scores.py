"""Live & recent scores.

A thin, cached proxy over ESPN's public scoreboard JSON (no API key needed) so
the app has a live "what's happening now" surface — today's games are tomorrow's
Daily Calls. Best-effort: any failure degrades to an empty list so the app never
breaks on a flaky upstream.
"""
from __future__ import annotations

import logging
import time

import httpx
from fastapi import APIRouter, Query

logger = logging.getLogger("oaksy.scores")
router = APIRouter(prefix="/api/scores", tags=["scores"])

_ESPN = {
    "NFL": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
    "NBA": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    "MLB": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
}

# Cache each sport's normalized payload briefly so a burst of viewers hits ESPN
# at most once every few seconds.
_cache: dict[str, tuple[float, dict]] = {}
_TTL = 25.0


def _competitor(comp: dict, side: str) -> dict:
    for c in comp.get("competitors", []):
        if c.get("homeAway") == side:
            team = c.get("team", {})
            return {
                "abbr": team.get("abbreviation") or team.get("shortDisplayName") or "—",
                "name": team.get("shortDisplayName") or team.get("displayName") or "",
                "logo": team.get("logo"),
                "score": c.get("score"),
                "winner": bool(c.get("winner")),
            }
    return {"abbr": "—", "name": "", "logo": None, "score": None, "winner": False}


def _normalize(raw: dict) -> list[dict]:
    games: list[dict] = []
    for event in raw.get("events", []):
        comps = event.get("competitions") or []
        if not comps:
            continue
        comp = comps[0]
        status = (event.get("status") or {}).get("type", {})
        situation = comp.get("situation") or {}
        games.append(
            {
                "id": event.get("id"),
                "state": status.get("state"),  # pre | in | post
                "detail": status.get("shortDetail") or status.get("detail") or "",
                "start": event.get("date"),
                "home": _competitor(comp, "home"),
                "away": _competitor(comp, "away"),
                # A short live note when ESPN provides one (e.g. "2nd & 7 at NE 30").
                "note": situation.get("downDistanceText") or situation.get("lastPlay", {}).get("text"),
            }
        )
    # Live games first, then upcoming, then finals.
    order = {"in": 0, "pre": 1, "post": 2}
    games.sort(key=lambda g: order.get(g["state"], 3))
    return games


@router.get("")
def scores(sport: str = Query(default="MLB")):
    sport = sport.upper()
    url = _ESPN.get(sport)
    if not url:
        return {"sport": sport, "games": [], "note": "Unsupported sport."}

    hit = _cache.get(sport)
    if hit and (time.monotonic() - hit[0]) < _TTL:
        return hit[1]

    try:
        resp = httpx.get(url, timeout=8, headers={"User-Agent": "Oaksy/1.0"})
        resp.raise_for_status()
        games = _normalize(resp.json())
        payload = {"sport": sport, "games": games}
    except Exception as exc:  # upstream down/slow/changed — never break the app
        logger.warning("Scores fetch failed for %s: %s", sport, exc)
        payload = {"sport": sport, "games": [], "note": "Scores are taking a break — check back soon."}

    _cache[sport] = (time.monotonic(), payload)
    return payload
