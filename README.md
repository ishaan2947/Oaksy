# Oaksy

**The arena where fans out-coach the coach — and settle it with data.**

Oaksy is a software-only, fan-focused sports app (no betting). Every day, one
real game decision drops. You have 30 seconds and a few choices. Then you see
what the coach actually did, the outcome, an AI-backed verdict, and how you
stack up against everyone else — and the best arguments fight it out in the
weekly Debate Arena.

This repo contains a working **v1 MVP**: a Python/FastAPI backend and a React
(Vite) web frontend, built in the order laid out in the product spec.

---

## What's in the box (v1)

| Mode / Feature | Status | Where |
|---|---|---|
| 🏈 **The Daily Call** — one real situation, 30s timer, tap your call, reveal | ✅ | `frontend/src/components/DailyCall.jsx`, `backend/app/routers/situations.py` |
| **AI verdict** — Claude explains whether the data backed the coach (graceful fallback) | ✅ | `backend/app/ai.py` |
| **Community split** — "53% punted" after every call | ✅ | `backend/app/services.py` |
| 🏆 **Coach Score** — your running record vs real coaches + rank | ✅ | `backend/app/routers/users.py` |
| **Shareable result card** — the growth engine, screenshot-worthy | ✅ | `frontend/src/components/ShareCard.jsx` |
| ⚔️ **Debate Arena** — weekly bracket, vote on the best reasoning | ✅ | `backend/app/routers/debates.py` |
| **Auth** — email/password, JWT (no OAuth in v1) | ✅ | `backend/app/routers/auth.py` |
| **Data pipeline** — real NFL 4th-down decisions from nflverse | ✅ | `backend/scripts/pull_nfl.py` |
| 82-0 GM Mode | ⛔ v2 (per spec) | — |
| Live in-game decisions | ⛔ v2 (needs paid real-time data) | — |
| Public social feed | ⛔ never (social *mechanics* instead) | — |

The app ships seeded with **10 curated, real decision moments** (NFL + NBA) so it
has rich content the moment you boot it.

---

## Tech stack

| Layer | Tech |
|---|---|
| Web frontend | React 18 + Vite |
| Backend | FastAPI + Python 3.13 |
| ORM / DB | SQLAlchemy 2 — **SQLite by default**, Postgres-ready via one env var |
| AI verdict | Anthropic Claude (`claude-sonnet-4-6`, per spec) — optional |
| Data source | [nflverse](https://github.com/nflverse/nflverse-data) play-by-play (free) |

> **Two pragmatic defaults**, both swappable: the app uses **SQLite** so it runs
> with zero external setup, and the AI layer **gracefully falls back** to the
> stored analytics verdict when no Claude API key is configured. Add Postgres
> and/or a key whenever you want — nothing else changes.

---

## Quickstart

You need **Python 3.11+** and **Node 18+**. Two terminals.

### 1) Backend (terminal A)

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate       macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # optional — defaults work as-is
uvicorn app.main:app --reload --port 8000
```

The API comes up at <http://localhost:8000>, auto-creates the SQLite DB, and
seeds the 10 curated situations on first boot. Interactive API docs:
<http://localhost:8000/docs>.

### 2) Frontend (terminal B)

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The dev server proxies `/api` to the backend, so
there's no CORS setup to do.

That's it — pick a call, see the verdict, share the card, sign up to track your
Coach Score, and vote in the Debate Arena.

---

## Configuration

All optional — see `backend/.env.example`.

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./oaksy.db` | Swap for Postgres (see below) |
| `ANTHROPIC_API_KEY` | _(empty)_ | Enable real Claude verdicts |
| `AI_MODEL` | `claude-sonnet-4-6` | Verdict model |
| `SECRET_KEY` | `dev-secret-change-me` | **Change in production** — signs JWTs |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed frontend origins |

### Using Postgres instead of SQLite

```bash
docker compose up -d                       # starts Postgres on :5432
pip install "psycopg[binary]"              # in the backend venv
# backend/.env:
DATABASE_URL=postgresql+psycopg://oaksy:oaksy@localhost:5432/oaksy
```

Restart the backend — tables are created and seeded automatically.

### Enabling the AI verdict layer

Put a key in `backend/.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

New situations (seed + pipeline) get a Claude-written verdict; without a key the
app uses the stored analytics note. `GET /api/health` reports `ai_enabled`.

---

## The data pipeline

Pull real NFL 4th-down decision moments straight from nflverse into the same DB:

```bash
cd backend
python scripts/pull_nfl.py --season 2023 --limit 40
python scripts/pull_nfl.py --season 2023 --limit 40 --ai   # also write Claude verdicts
```

It downloads the free play-by-play file, finds high-leverage 4th downs (2nd half,
one-score games), and stores them as Daily-Call situations. The "best call" is a
transparent, documented heuristic — swap in a real EPA/win-probability model for
production (noted in the script).

---

## API overview

| Method | Path | Notes |
|---|---|---|
| `GET` | `/api/health` | Status + whether AI is enabled |
| `GET` | `/api/situations/daily?sport=NFL` | Today's Daily Call (answer hidden) |
| `GET` | `/api/situations/{id}/reveal` | Verdict + community split |
| `POST` | `/api/picks` | Submit a call → returns the full reveal |
| `POST` | `/api/auth/signup` · `/login` · `GET /me` | Email/password + JWT |
| `GET` | `/api/users/me/score` | Your Coach Score |
| `GET` | `/api/users/leaderboard` | Top coaches |
| `GET` | `/api/debate/current` | This week's Debate Arena |
| `POST` | `/api/debate/posts/{pick_id}/vote` | Upvote a reasoning (toggle) |

Anonymous users can play and vote in the split via a client-generated `anon_id`;
signing in is what builds a persistent Coach Score and lets you vote in debates.

---

## Project layout

```
Oaksy/
├─ backend/
│  ├─ app/
│  │  ├─ main.py          # FastAPI app, CORS, startup seeding
│  │  ├─ models.py        # Situation, User, Pick, DebateVote
│  │  ├─ routers/         # auth, situations, picks, users, debates
│  │  ├─ services.py      # community split, daily selection, reveal
│  │  ├─ ai.py            # Claude verdict (graceful fallback)
│  │  ├─ seed_data.py     # 10 curated real situations
│  │  └─ seed.py          # idempotent seeding
│  ├─ scripts/pull_nfl.py # nflverse data pipeline
│  └─ requirements.txt
├─ frontend/
│  └─ src/
│     ├─ App.jsx          # tabs: Daily Call · Debate Arena · Coach Score
│     ├─ api.js, auth.jsx
│     └─ components/       # DailyCall, Timer, RevealCard, ShareCard, …
├─ docker-compose.yml     # optional Postgres
└─ README.md
```

---

## Design direction

Dark-first "sports coliseum meets modern game UI": deep blacks, oversized
numerals, a pulsing 30-second timer, green when you beat the coach, red when you
didn't, gold for Debate wins, and result cards built to look great as a
screenshot. No generic AI aesthetic, no chat bubbles, no pastel gradients.

---

## Notes & next steps

- **Curated seed data** is simplified for a fan audience; the pipeline produces
  objectively-sourced situations. Wire a real EPA/WP model into `pull_nfl.py`
  for production-grade "best call" labels.
- The smoke test (`backend/smoke_test.py`) exercises the whole API end-to-end.
- Suggested v2, in spec order: 82-0 GM Mode (needs a player DB), live in-game
  decisions (paid real-time data), React Native mobile (shares this codebase).
