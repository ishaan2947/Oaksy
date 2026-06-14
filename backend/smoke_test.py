"""Throwaway end-to-end smoke test against the Oaksy API via TestClient."""
import os
import uuid

# Use an isolated throwaway DB so we don't clobber a real one.
os.environ["DATABASE_URL"] = "sqlite:///./smoke.db"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

c = TestClient(app)


def check(label, cond):
    print(("PASS" if cond else "FAIL"), label)
    assert cond, label


with c:  # triggers lifespan (tables + seed)
    h = c.get("/api/health").json()
    check(f"health ok (ai_enabled={h['ai_enabled']})", h["status"] == "ok")

    daily = c.get("/api/situations/daily?sport=NFL").json()
    check("daily call returned", "id" in daily and daily["situation_description"])
    check("daily call hides answer", "actual_call" not in daily)
    sid = daily["id"]

    nba = c.get("/api/situations/daily?sport=NBA").json()
    check("NBA daily call returned", "id" in nba)

    # Anonymous pick
    anon = str(uuid.uuid4())
    r = c.post("/api/picks", json={"situation_id": sid, "choice": "a", "anon_id": anon}).json()
    check("anon pick reveal has verdict", bool(r["ai_verdict"]))
    check("community split counts the pick", r["community_split"]["total"] >= 1)

    # Signup
    email = f"coach_{uuid.uuid4().hex[:8]}@oaksy.app"
    tok = c.post("/api/auth/signup", json={
        "email": email, "display_name": "TestCoach", "password": "hunter2hunter2",
    }).json()
    check("signup returns token", "access_token" in tok)
    auth = {"Authorization": f"Bearer {tok['access_token']}"}

    me = c.get("/api/auth/me", headers=auth).json()
    check("me returns user", me["email"] == email)

    # Authed pick with reasoning
    r2 = c.post("/api/picks", headers=auth, json={
        "situation_id": sid, "choice": daily["options"][0]["key"],
        "reasoning": "The win probability math backs keeping the offense on the field.",
    }).json()
    check("authed pick has your_choice", r2["your_choice"] is not None)

    # Coach score
    score = c.get("/api/users/me/score", headers=auth).json()
    check(f"coach score computed (win_rate={score['win_rate']}, rank={score['rank_label']})",
          score["total_calls"] == 1)

    # A second user votes in the debate arena
    tok2 = c.post("/api/auth/signup", json={
        "email": f"v_{uuid.uuid4().hex[:8]}@oaksy.app", "display_name": "Voter",
        "password": "voterpass123",
    }).json()
    auth2 = {"Authorization": f"Bearer {tok2['access_token']}"}

    arena = c.get("/api/debate/current", headers=auth2).json()
    check("debate arena returns situations", len(arena["situations"]) >= 1)
    posts = arena["situations"][0]["posts"]
    check("debate has a reasoning post", len(posts) >= 1)

    pick_id = posts[0]["pick_id"]
    v = c.post(f"/api/debate/posts/{pick_id}/vote", headers=auth2).json()
    check("vote registered", v["you_voted"] is True and v["votes"] >= 1)

    # Leaderboard
    lb = c.get("/api/users/leaderboard").json()
    check("leaderboard returns entries", len(lb) >= 1)

print("\nALL SMOKE TESTS PASSED")
