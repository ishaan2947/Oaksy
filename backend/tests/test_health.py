def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["ai_enabled"] is False  # forced off in tests


def test_daily_hides_answer(client, daily):
    assert "id" in daily and daily["situation_description"]
    # The answer must never leak in the playable card.
    for leaked in ("actual_call", "best_call", "outcome", "ai_verdict"):
        assert leaked not in daily


def test_daily_both_sports(client):
    assert client.get("/api/situations/daily?sport=NFL").json()["sport"] == "NFL"
    assert client.get("/api/situations/daily?sport=NBA").json()["sport"] == "NBA"
