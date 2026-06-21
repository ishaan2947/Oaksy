def _legal_five(pool):
    """Greedy: cheapest guard + cheapest center + 3 cheapest others."""
    guards = sorted((p for p in pool if p["pos"] == "G"), key=lambda p: p["cost"])
    centers = sorted((p for p in pool if p["pos"] == "C"), key=lambda p: p["cost"])
    chosen = {guards[0]["id"], centers[0]["id"]}
    rest = sorted((p for p in pool if p["id"] not in chosen), key=lambda p: p["cost"])
    five = [guards[0], centers[0]] + rest[:3]
    return [p["id"] for p in five]


def test_spin_shape(client):
    s = client.post("/api/gm/spin").json()
    assert len(s["pool"]) == 12
    assert s["cap"] == 32 and s["roster_size"] == 5
    assert "cap" in s["rules"]


def test_submit_scores_team(client, make_user):
    headers, _ = make_user("GM")
    s = client.post("/api/gm/spin", headers=headers).json()
    ids = _legal_five(s["pool"])
    r = client.post(
        "/api/gm/submit", headers=headers, json={"spin_id": s["spin_id"], "player_ids": ids}
    )
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["score"] <= 100
    assert body["verdict"]
    assert "Can you beat it?" in body["share_line"]
    assert body["total_cost"] <= body["cap"]

    score = client.get("/api/users/me/score", headers=headers).json()
    assert score["gm_teams"] == 1
    assert score["gm_rating"] > 0


def test_rejects_wrong_roster_size(client):
    s = client.post("/api/gm/spin").json()
    ids = _legal_five(s["pool"])[:4]
    r = client.post("/api/gm/submit", json={"spin_id": s["spin_id"], "player_ids": ids})
    assert r.status_code == 400


def test_rejects_player_outside_spin(client):
    from app.players import PLAYERS

    s = client.post("/api/gm/spin").json()
    pool_ids = {p["id"] for p in s["pool"]}
    outsider = next(p["id"] for p in PLAYERS if p["id"] not in pool_ids)
    ids = [outsider] + _legal_five(s["pool"])[1:]
    r = client.post("/api/gm/submit", json={"spin_id": s["spin_id"], "player_ids": ids})
    assert r.status_code == 400


def test_rejects_unknown_spin(client):
    r = client.post("/api/gm/submit", json={"spin_id": "nope", "player_ids": ["jordan"]})
    assert r.status_code in (400, 404)
