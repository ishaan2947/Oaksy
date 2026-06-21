import uuid


def test_join_and_count(client):
    before = client.get("/api/waitlist/count").json()["count"]
    email = f"{uuid.uuid4().hex[:10]}@oaksy.app"

    r = client.post("/api/waitlist", json={"email": email, "source": "landing"})
    assert r.status_code == 201
    body = r.json()
    assert body["ok"] is True
    assert body["already"] is False
    assert body["count"] == before + 1


def test_join_is_idempotent(client):
    email = f"{uuid.uuid4().hex[:10]}@oaksy.app"
    client.post("/api/waitlist", json={"email": email})
    count_after_first = client.get("/api/waitlist/count").json()["count"]

    again = client.post("/api/waitlist", json={"email": email})
    assert again.status_code == 201
    assert again.json()["already"] is True
    # no new row added
    assert client.get("/api/waitlist/count").json()["count"] == count_after_first


def test_invalid_email_rejected(client):
    assert client.post("/api/waitlist", json={"email": "not-an-email"}).status_code == 422


def test_email_is_case_insensitive(client):
    base = uuid.uuid4().hex[:10]
    client.post("/api/waitlist", json={"email": f"{base}@oaksy.app"})
    c = client.get("/api/waitlist/count").json()["count"]
    dupe = client.post("/api/waitlist", json={"email": f"{base.upper()}@OAKSY.APP"})
    assert dupe.json()["already"] is True
    assert client.get("/api/waitlist/count").json()["count"] == c
