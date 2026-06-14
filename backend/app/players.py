"""Curated NBA legend pool for 82-0 GM Mode.

Each player has a position bucket (G/F/C), an era, a salary-cap cost (4-10),
and a one-line tag. Costs encode tier so you can't just stack five 10s under
the cap — you balance superstars with cheaper role legends.

Curated for the MVP — swap in a real source (Basketball Reference, etc.) later.
"""
from __future__ import annotations

# id, name, pos (G/F/C), era, cost (4-10), tag
PLAYERS: list[dict] = [
    # ----- Guards -----
    {"id": "jordan", "name": "Michael Jordan", "pos": "G", "era": "1990s", "cost": 10, "tag": "Six rings, zero fear."},
    {"id": "magic", "name": "Magic Johnson", "pos": "G", "era": "1980s", "cost": 10, "tag": "6'9\" point god."},
    {"id": "curry", "name": "Stephen Curry", "pos": "G", "era": "2010s", "cost": 10, "tag": "Broke the geometry of the game."},
    {"id": "kobe", "name": "Kobe Bryant", "pos": "G", "era": "2000s", "cost": 9, "tag": "Mamba mentality."},
    {"id": "oscar", "name": "Oscar Robertson", "pos": "G", "era": "1960s", "cost": 9, "tag": "Averaged a triple-double."},
    {"id": "west", "name": "Jerry West", "pos": "G", "era": "1970s", "cost": 8, "tag": "Literally the logo."},
    {"id": "wade", "name": "Dwyane Wade", "pos": "G", "era": "2000s", "cost": 8, "tag": "Flash in the clutch."},
    {"id": "harden", "name": "James Harden", "pos": "G", "era": "2010s", "cost": 8, "tag": "Step-back maestro."},
    {"id": "iverson", "name": "Allen Iverson", "pos": "G", "era": "2000s", "cost": 7, "tag": "Pound-for-pound nightmare."},
    {"id": "nash", "name": "Steve Nash", "pos": "G", "era": "2000s", "cost": 7, "tag": "Seven seconds or less."},
    {"id": "stockton", "name": "John Stockton", "pos": "G", "era": "1990s", "cost": 7, "tag": "All-time assists king."},
    {"id": "isiah", "name": "Isiah Thomas", "pos": "G", "era": "1980s", "cost": 7, "tag": "Bad Boy floor general."},
    {"id": "cp3", "name": "Chris Paul", "pos": "G", "era": "2010s", "cost": 7, "tag": "The Point God."},
    {"id": "drexler", "name": "Clyde Drexler", "pos": "G", "era": "1990s", "cost": 6, "tag": "The Glide."},
    {"id": "payton", "name": "Gary Payton", "pos": "G", "era": "1990s", "cost": 5, "tag": "The Glove — elite on-ball D."},
    {"id": "frazier", "name": "Walt Frazier", "pos": "G", "era": "1970s", "cost": 5, "tag": "Clyde, cool under pressure."},
    {"id": "miller", "name": "Reggie Miller", "pos": "G", "era": "1990s", "cost": 5, "tag": "Knicks' worst nightmare."},

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
    {"id": "pierce", "name": "Paul Pierce", "pos": "F", "era": "2000s", "cost": 6, "tag": "The Truth."},
    {"id": "melo", "name": "Carmelo Anthony", "pos": "F", "era": "2010s", "cost": 5, "tag": "Bucket-getting savant."},
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
    {"id": "moses", "name": "Moses Malone", "pos": "C", "era": "1980s", "cost": 7, "tag": "Fo', fo', fo'."},
    {"id": "ewing", "name": "Patrick Ewing", "pos": "C", "era": "1990s", "cost": 6, "tag": "Knicks' anchor."},
    {"id": "dwight", "name": "Dwight Howard", "pos": "C", "era": "2010s", "cost": 5, "tag": "Superman in the paint."},
    {"id": "unseld", "name": "Wes Unseld", "pos": "C", "era": "1970s", "cost": 4, "tag": "Outlet-pass and screen master."},
]

BY_ID: dict[str, dict] = {p["id"]: p for p in PLAYERS}

# Elite floor-spacers (used by the fallback scoring heuristic).
SHOOTERS = {"curry", "bird", "nash", "dirk", "durant", "miller", "harden"}

ELITE = {p["id"] for p in PLAYERS if p["cost"] >= 9}
