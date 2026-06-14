"""NBA legend pool for 82-0 GM Mode.

Each player: position bucket (G/F/C), era, salary-cap cost (4-10), one-line tag.
Costs encode tier so you can't stack five 10s under the cap — you balance
superstars with cheaper role legends.

The pool is **data-driven**: the curated list below is the base, and any extra
players in `app/players_custom.json` (produced by `scripts/import_players.py`)
are merged in at import time. Curated for the MVP — grow it from a real source
via the importer.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger("oaksy.players")

# id, name, pos (G/F/C), era, cost (4-10), tag
PLAYERS: list[dict] = [
    # ----- Guards -----
    {"id": "jordan", "name": "Michael Jordan", "pos": "G", "era": "1990s", "cost": 10, "tag": "Six rings, zero fear."},
    {"id": "magic", "name": "Magic Johnson", "pos": "G", "era": "1980s", "cost": 10, "tag": "6'9\" point god."},
    {"id": "curry", "name": "Stephen Curry", "pos": "G", "era": "2010s", "cost": 10, "tag": "Broke the geometry of the game."},
    {"id": "kobe", "name": "Kobe Bryant", "pos": "G", "era": "2000s", "cost": 9, "tag": "Mamba mentality."},
    {"id": "oscar", "name": "Oscar Robertson", "pos": "G", "era": "1960s", "cost": 9, "tag": "Averaged a triple-double."},
    {"id": "luka", "name": "Luka Doncic", "pos": "G", "era": "2020s", "cost": 9, "tag": "Step-back, stat-sheet stuffer."},
    {"id": "west", "name": "Jerry West", "pos": "G", "era": "1970s", "cost": 8, "tag": "Literally the logo."},
    {"id": "wade", "name": "Dwyane Wade", "pos": "G", "era": "2000s", "cost": 8, "tag": "Flash in the clutch."},
    {"id": "harden", "name": "James Harden", "pos": "G", "era": "2010s", "cost": 8, "tag": "Step-back maestro."},
    {"id": "iverson", "name": "Allen Iverson", "pos": "G", "era": "2000s", "cost": 7, "tag": "Pound-for-pound nightmare."},
    {"id": "nash", "name": "Steve Nash", "pos": "G", "era": "2000s", "cost": 7, "tag": "Seven seconds or less."},
    {"id": "stockton", "name": "John Stockton", "pos": "G", "era": "1990s", "cost": 7, "tag": "All-time assists king."},
    {"id": "isiah", "name": "Isiah Thomas", "pos": "G", "era": "1980s", "cost": 7, "tag": "Bad Boy floor general."},
    {"id": "cp3", "name": "Chris Paul", "pos": "G", "era": "2010s", "cost": 7, "tag": "The Point God."},
    {"id": "westbrook", "name": "Russell Westbrook", "pos": "G", "era": "2010s", "cost": 7, "tag": "Triple-double tornado."},
    {"id": "lillard", "name": "Damian Lillard", "pos": "G", "era": "2010s", "cost": 7, "tag": "Dame Time from the logo."},
    {"id": "kidd", "name": "Jason Kidd", "pos": "G", "era": "2000s", "cost": 7, "tag": "Triple-double floor general."},
    {"id": "kyrie", "name": "Kyrie Irving", "pos": "G", "era": "2010s", "cost": 7, "tag": "Handles from another planet."},
    {"id": "tmac", "name": "Tracy McGrady", "pos": "G", "era": "2000s", "cost": 7, "tag": "13 points in 33 seconds."},
    {"id": "gervin", "name": "George Gervin", "pos": "G", "era": "1980s", "cost": 7, "tag": "The Iceman's finger roll."},
    {"id": "drexler", "name": "Clyde Drexler", "pos": "G", "era": "1990s", "cost": 6, "tag": "The Glide."},
    {"id": "rayallen", "name": "Ray Allen", "pos": "G", "era": "2000s", "cost": 6, "tag": "Greatest shooter of his era."},
    {"id": "klay", "name": "Klay Thompson", "pos": "G", "era": "2010s", "cost": 6, "tag": "Splash Brother, 37 in a quarter."},
    {"id": "maravich", "name": "Pete Maravich", "pos": "G", "era": "1970s", "cost": 6, "tag": "Pistol Pete, showtime before Showtime."},
    {"id": "cousy", "name": "Bob Cousy", "pos": "G", "era": "1960s", "cost": 6, "tag": "The Houdini of the Hardwood."},
    {"id": "parker", "name": "Tony Parker", "pos": "G", "era": "2000s", "cost": 6, "tag": "Tear-drop in the lane."},
    {"id": "payton", "name": "Gary Payton", "pos": "G", "era": "1990s", "cost": 5, "tag": "The Glove — elite on-ball D."},
    {"id": "frazier", "name": "Walt Frazier", "pos": "G", "era": "1970s", "cost": 5, "tag": "Clyde, cool under pressure."},
    {"id": "miller", "name": "Reggie Miller", "pos": "G", "era": "1990s", "cost": 5, "tag": "Knicks' worst nightmare."},
    {"id": "ginobili", "name": "Manu Ginobili", "pos": "G", "era": "2000s", "cost": 5, "tag": "Euro-step innovator off the bench."},

    # ----- Forwards -----
    {"id": "lebron", "name": "LeBron James", "pos": "F", "era": "2010s", "cost": 10, "tag": "Freight train with a jumper."},
    {"id": "bird", "name": "Larry Bird", "pos": "F", "era": "1980s", "cost": 10, "tag": "Trash talk, then the dagger."},
    {"id": "durant", "name": "Kevin Durant", "pos": "F", "era": "2010s", "cost": 9, "tag": "Unguardable 7-foot scorer."},
    {"id": "giannis", "name": "Giannis Antetokounmpo", "pos": "F", "era": "2020s", "cost": 9, "tag": "Greek Freak two-way force."},
    {"id": "duncan", "name": "Tim Duncan", "pos": "F", "era": "2000s", "cost": 9, "tag": "The Big Fundamental."},
    {"id": "kawhi", "name": "Kawhi Leonard", "pos": "F", "era": "2010s", "cost": 8, "tag": "The Claw — two-way assassin."},
    {"id": "dr-j", "name": "Julius Erving", "pos": "F", "era": "1980s", "cost": 8, "tag": "Brought flight to the game."},
    {"id": "malone", "name": "Karl Malone", "pos": "F", "era": "1990s", "cost": 8, "tag": "The Mailman delivers."},
    {"id": "dirk", "name": "Dirk Nowitzki", "pos": "F", "era": "2000s", "cost": 8, "tag": "Unblockable one-legged fade."},
    {"id": "barkley", "name": "Charles Barkley", "pos": "F", "era": "1990s", "cost": 8, "tag": "The Round Mound of Rebound."},
    {"id": "kg", "name": "Kevin Garnett", "pos": "F", "era": "2000s", "cost": 8, "tag": "Anything is possible!"},
    {"id": "pippen", "name": "Scottie Pippen", "pos": "F", "era": "1990s", "cost": 7, "tag": "Best wing defender ever."},
    {"id": "baylor", "name": "Elgin Baylor", "pos": "F", "era": "1960s", "cost": 7, "tag": "Original highlight machine."},
    {"id": "nique", "name": "Dominique Wilkins", "pos": "F", "era": "1980s", "cost": 7, "tag": "The Human Highlight Film."},
    {"id": "mchale", "name": "Kevin McHale", "pos": "F", "era": "1980s", "cost": 7, "tag": "Lowest of low-post footwork."},
    {"id": "pettit", "name": "Bob Pettit", "pos": "F", "era": "1960s", "cost": 7, "tag": "First-ever MVP, relentless glass."},
    {"id": "tatum", "name": "Jayson Tatum", "pos": "F", "era": "2020s", "cost": 7, "tag": "Modern two-way wing scorer."},
    {"id": "pierce", "name": "Paul Pierce", "pos": "F", "era": "2000s", "cost": 6, "tag": "The Truth."},
    {"id": "worthy", "name": "James Worthy", "pos": "F", "era": "1980s", "cost": 6, "tag": "Big Game James."},
    {"id": "gasol", "name": "Pau Gasol", "pos": "F", "era": "2000s", "cost": 6, "tag": "Skilled big, two-time champ."},
    {"id": "pg13", "name": "Paul George", "pos": "F", "era": "2010s", "cost": 6, "tag": "Playoff P, two-way wing."},
    {"id": "melo", "name": "Carmelo Anthony", "pos": "F", "era": "2010s", "cost": 5, "tag": "Bucket-getting savant."},
    {"id": "kemp", "name": "Shawn Kemp", "pos": "F", "era": "1990s", "cost": 5, "tag": "The Reign Man's thunder."},
    {"id": "granthill", "name": "Grant Hill", "pos": "F", "era": "2000s", "cost": 5, "tag": "Smooth all-around forward."},
    {"id": "draymond", "name": "Draymond Green", "pos": "F", "era": "2010s", "cost": 5, "tag": "Defensive QB, point-forward glue."},
    {"id": "rodman", "name": "Dennis Rodman", "pos": "F", "era": "1990s", "cost": 4, "tag": "Rebounding + defense cheat code."},

    # ----- Centers -----
    {"id": "kareem", "name": "Kareem Abdul-Jabbar", "pos": "C", "era": "1980s", "cost": 10, "tag": "Unstoppable skyhook."},
    {"id": "wilt", "name": "Wilt Chamberlain", "pos": "C", "era": "1960s", "cost": 10, "tag": "Scored 100 in a game."},
    {"id": "shaq", "name": "Shaquille O'Neal", "pos": "C", "era": "2000s", "cost": 10, "tag": "Most dominant force ever."},
    {"id": "russell", "name": "Bill Russell", "pos": "C", "era": "1960s", "cost": 9, "tag": "11 rings, defensive GOAT."},
    {"id": "hakeem", "name": "Hakeem Olajuwon", "pos": "C", "era": "1990s", "cost": 9, "tag": "The Dream Shake."},
    {"id": "jokic", "name": "Nikola Jokic", "pos": "C", "era": "2020s", "cost": 9, "tag": "Point-center passing wizard."},
    {"id": "robinson", "name": "David Robinson", "pos": "C", "era": "1990s", "cost": 8, "tag": "The Admiral."},
    {"id": "embiid", "name": "Joel Embiid", "pos": "C", "era": "2020s", "cost": 8, "tag": "Trust the Process."},
    {"id": "ad", "name": "Anthony Davis", "pos": "C", "era": "2010s", "cost": 8, "tag": "The Brow — unicorn rim protector."},
    {"id": "moses", "name": "Moses Malone", "pos": "C", "era": "1980s", "cost": 7, "tag": "Fo', fo', fo'."},
    {"id": "wemby", "name": "Victor Wembanyama", "pos": "C", "era": "2020s", "cost": 7, "tag": "Generational two-way unicorn."},
    {"id": "ewing", "name": "Patrick Ewing", "pos": "C", "era": "1990s", "cost": 6, "tag": "Knicks' anchor."},
    {"id": "walton", "name": "Bill Walton", "pos": "C", "era": "1970s", "cost": 6, "tag": "Passing-big maestro."},
    {"id": "mourning", "name": "Alonzo Mourning", "pos": "C", "era": "1990s", "cost": 6, "tag": "Zo's shot-blocking ferocity."},
    {"id": "yao", "name": "Yao Ming", "pos": "C", "era": "2000s", "cost": 6, "tag": "7'6\" skilled giant."},
    {"id": "gilmore", "name": "Artis Gilmore", "pos": "C", "era": "1970s", "cost": 6, "tag": "The A-Train, elite efficiency."},
    {"id": "reed", "name": "Willis Reed", "pos": "C", "era": "1970s", "cost": 6, "tag": "Captain Clutch."},
    {"id": "kat", "name": "Karl-Anthony Towns", "pos": "C", "era": "2020s", "cost": 6, "tag": "Stretch-five sharpshooter."},
    {"id": "dwight", "name": "Dwight Howard", "pos": "C", "era": "2010s", "cost": 5, "tag": "Superman in the paint."},
    {"id": "parish", "name": "Robert Parish", "pos": "C", "era": "1980s", "cost": 5, "tag": "The Chief — durable anchor."},
    {"id": "mutombo", "name": "Dikembe Mutombo", "pos": "C", "era": "1990s", "cost": 5, "tag": "Finger wag, defensive titan."},
    {"id": "benwallace", "name": "Ben Wallace", "pos": "C", "era": "2000s", "cost": 5, "tag": "Undrafted Defensive-POY force."},
    {"id": "gobert", "name": "Rudy Gobert", "pos": "C", "era": "2020s", "cost": 5, "tag": "Stifle Tower rim protection."},
    {"id": "unseld", "name": "Wes Unseld", "pos": "C", "era": "1970s", "cost": 4, "tag": "Outlet-pass and screen master."},
]


def _merge_custom() -> None:
    """Merge app/players_custom.json (from the importer) into PLAYERS, by id."""
    path = Path(__file__).with_name("players_custom.json")
    if not path.exists():
        return
    try:
        extra = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Could not read players_custom.json: %s", exc)
        return
    known = {p["id"] for p in PLAYERS}
    required = {"id", "name", "pos", "era", "cost", "tag"}
    added = 0
    for row in extra:
        if not required.issubset(row) or row["pos"] not in ("G", "F", "C"):
            continue
        if row["id"] in known:
            continue
        PLAYERS.append({k: row[k] for k in ("id", "name", "pos", "era", "cost", "tag")})
        known.add(row["id"])
        added += 1
    if added:
        logger.info("Merged %d custom player(s) from players_custom.json", added)


_merge_custom()

BY_ID: dict[str, dict] = {p["id"]: p for p in PLAYERS}

# Elite floor-spacers (used by the fallback scoring heuristic).
SHOOTERS = {
    "curry", "bird", "nash", "dirk", "durant", "miller", "harden",
    "lillard", "rayallen", "klay", "kat",
}

ELITE = {p["id"] for p in PLAYERS if p["cost"] >= 9}
