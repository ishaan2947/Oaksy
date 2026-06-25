def test_submit_and_summary(client):
    before = client.get("/api/feedback/summary").json()["total"]

    r = client.post("/api/feedback", json={"rating": "yes", "comment": "Love it"})
    assert r.status_code == 201
    body = r.json()
    assert body["total"] == before + 1
    assert body["yes"] >= 1

    # rating-only (no comment) is fine
    assert client.post("/api/feedback", json={"rating": "maybe"}).status_code == 201

    summary = client.get("/api/feedback/summary").json()
    assert summary["total"] == before + 2


def test_invalid_rating_rejected(client):
    assert client.post("/api/feedback", json={"rating": "love"}).status_code == 422
    assert client.post("/api/feedback", json={}).status_code == 422
