import uuid


def test_signup_login_me(client):
    email = f"{uuid.uuid4().hex[:10]}@oaksy.app"
    r = client.post(
        "/api/auth/signup",
        json={"email": email, "display_name": "Ace", "password": "password123"},
    )
    assert r.status_code == 201
    token = r.json()["access_token"]
    assert r.json()["user"]["email"] == email

    # login returns a token too
    r2 = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert r2.status_code == 200

    # /me requires the token
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200 and me.json()["display_name"] == "Ace"


def test_duplicate_email_conflicts(client):
    email = f"{uuid.uuid4().hex[:10]}@oaksy.app"
    body = {"email": email, "display_name": "A", "password": "password123"}
    assert client.post("/api/auth/signup", json=body).status_code == 201
    assert client.post("/api/auth/signup", json=body).status_code == 409


def test_bad_password_rejected(client):
    email = f"{uuid.uuid4().hex[:10]}@oaksy.app"
    client.post(
        "/api/auth/signup",
        json={"email": email, "display_name": "A", "password": "password123"},
    )
    r = client.post("/api/auth/login", json={"email": email, "password": "wrongpass1"})
    assert r.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/auth/me").status_code == 401


def test_short_password_validation(client):
    r = client.post(
        "/api/auth/signup",
        json={"email": "x@oaksy.app", "display_name": "A", "password": "short"},
    )
    assert r.status_code == 422
