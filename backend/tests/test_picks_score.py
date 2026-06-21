import uuid


def test_anon_pick_requires_anon_id(client, daily):
    r = client.post("/api/picks", json={"situation_id": daily["id"], "choice": "a"})
    assert r.status_code == 400


def test_anon_pick_reveal_and_split(client, daily):
    anon = str(uuid.uuid4())
    r = client.post(
        "/api/picks",
        json={"situation_id": daily["id"], "choice": "a", "anon_id": anon},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["your_choice"] == "a"
    assert body["ai_verdict"]  # fallback verdict is non-empty
    assert body["community_split"]["total"] >= 1
    # reveal now exposes the answer
    assert body["best_call"] in ("a", "b", "c")


def test_authed_pick_scores_and_streak(client, make_user, daily):
    headers, _ = make_user("Streaky")
    # learn the optimal call from a throwaway anon reveal
    reveal = client.post(
        "/api/picks",
        json={"situation_id": daily["id"], "choice": "a", "anon_id": str(uuid.uuid4())},
    ).json()
    best = reveal["best_call"]

    r = client.post(
        "/api/picks",
        headers=headers,
        json={"situation_id": daily["id"], "choice": best},
    )
    assert r.status_code == 201
    assert r.json()["you_were_correct"] is True

    score = client.get("/api/users/me/score", headers=headers).json()
    assert score["total_calls"] == 1
    assert score["correct_calls"] == 1
    assert score["win_rate"] == 100.0
    assert score["current_streak"] == 1  # played today
    assert score["longest_streak"] == 1


def test_pick_is_idempotent_per_user(client, make_user, daily):
    headers, _ = make_user()
    a = client.post(
        "/api/picks", headers=headers, json={"situation_id": daily["id"], "choice": "a"}
    )
    b = client.post(
        "/api/picks", headers=headers, json={"situation_id": daily["id"], "choice": "b"}
    )
    assert a.status_code == 201 and b.status_code == 201
    # second submit returns the original pick, not a new one
    assert a.json()["your_choice"] == b.json()["your_choice"] == "a"


def test_leaderboard(client, make_user, daily):
    headers, _ = make_user("Boarder")
    client.post("/api/picks", headers=headers, json={"situation_id": daily["id"], "choice": "a"})
    rows = client.get("/api/users/leaderboard").json()
    assert any(r["display_name"] == "Boarder" for r in rows)
