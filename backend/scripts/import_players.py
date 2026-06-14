"""Grow the 82-0 GM Mode legend pool from a CSV — no code edits required.

The base pool lives in `app/players.py`. This importer merges additional players
from a CSV into `app/players_custom.json`, which `players.py` auto-loads at boot.

Usage (from the backend/ directory):
    python scripts/import_players.py --csv players.csv
    python scripts/import_players.py --sources      # print free data sources

CSV columns (header required):  id,name,pos,era,cost,tag
    id    short unique slug, e.g. "lebron"
    name  display name
    pos   one of G / F / C
    era   e.g. "2010s"
    cost  salary-cap cost, integer 4-10 (tier: 10 = all-time GOAT, 4 = role legend)
    tag   one-line scouting note

Why a CSV and not a live scrape?
    Basketball-Reference prohibits scraping in its terms of use, and the free
    NBA endpoints are rate-limited and unstable. A CSV keeps the pipeline robust
    and lets you assemble data from any source you're permitted to use. See
    --sources for legitimate free options to build the CSV from.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.players import BY_ID  # noqa: E402  (base pool, for dedup)

CUSTOM_PATH = ROOT / "app" / "players_custom.json"
REQUIRED = ["id", "name", "pos", "era", "cost", "tag"]

SOURCES = """
Free / legitimate sources to build your players.csv from:

  • nba_api (https://github.com/swar/nba_api) — unofficial Python wrapper for
    stats.nba.com. Historical players via `players.get_players()`. Rate-limited;
    add delays. Great for names/positions; you assign era + cost yourself.

  • Ball Don't Lie API (https://www.balldontlie.io) — free tier (API key) with
    player + team data. Good for active/recent players.

  • Public domain / Kaggle datasets — e.g. historical NBA player stat dumps.
    Map columns to: id,name,pos,era,cost,tag.

Assign `cost` by tier (your call): 10 = inner-circle GOAT, 8-9 = clear top-tier,
6-7 = star, 4-5 = elite role player / specialist. Keep the pool balanced across
G / F / C so the wheel always yields a legal lineup.

NOTE: Do not scrape Basketball-Reference — its terms prohibit it.
"""


def load_custom() -> list[dict]:
    if CUSTOM_PATH.exists():
        try:
            return json.loads(CUSTOM_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Import GM Mode players from a CSV.")
    parser.add_argument("--csv", help="Path to a CSV with columns: " + ",".join(REQUIRED))
    parser.add_argument("--sources", action="store_true", help="Print free data sources and exit")
    parser.add_argument("--replace", action="store_true", help="Replace players_custom.json instead of merging")
    args = parser.parse_args()

    if args.sources or not args.csv:
        print(SOURCES)
        if not args.csv:
            return
        return

    path = Path(args.csv)
    if not path.exists():
        sys.exit(f"CSV not found: {path}")

    existing = {} if args.replace else {p["id"]: p for p in load_custom()}
    base_ids = set(BY_ID)

    added, skipped = 0, 0
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"CSV missing columns: {', '.join(missing)}")
        for i, row in enumerate(reader, start=2):
            pid = (row.get("id") or "").strip()
            pos = (row.get("pos") or "").strip().upper()
            if not pid or pos not in ("G", "F", "C"):
                print(f"  line {i}: skipped (bad id/pos)")
                skipped += 1
                continue
            if pid in base_ids:
                print(f"  line {i}: skipped ('{pid}' already in base pool)")
                skipped += 1
                continue
            try:
                cost = max(1, min(10, int(float(row["cost"]))))
            except (ValueError, KeyError):
                print(f"  line {i}: skipped (bad cost)")
                skipped += 1
                continue
            existing[pid] = {
                "id": pid,
                "name": (row.get("name") or pid).strip(),
                "pos": pos,
                "era": (row.get("era") or "").strip(),
                "cost": cost,
                "tag": (row.get("tag") or "").strip(),
            }
            added += 1

    merged = list(existing.values())
    CUSTOM_PATH.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(f"\nWrote {len(merged)} custom player(s) to {CUSTOM_PATH.name} "
          f"(+{added} this run, {skipped} skipped).")
    print("Restart the backend to load them into the wheel.")


if __name__ == "__main__":
    main()
