def test_debate_surfaces_reasoning_and_voting(client, make_user, daily):
    author, _ = make_user("Arguer")
    voter, _ = make_user("Voter")

    # An authed pick WITH reasoning becomes a debate post.
    client.post(
        "/api/picks",
        headers=author,
        json={
            "situation_id": daily["id"],
            "choice": "a",
            "reasoning": "Field-position math favors this call.",
        },
    )

    arena = client.get("/api/debate/current").json()
    assert arena["week_label"]
    sit = next((s for s in arena["situations"] if s["situation_id"] == daily["id"]), None)
    assert sit is not None
    post = next((p for p in sit["posts"] if p["author"] == "Arguer"), None)
    assert post is not None and post["votes"] == 0

    # Another user upvotes it.
    v = client.post(f"/api/debate/posts/{post['pick_id']}/vote", headers=voter).json()
    assert v["you_voted"] is True and v["votes"] == 1

    # Voting again toggles it off.
    v2 = client.post(f"/api/debate/posts/{post['pick_id']}/vote", headers=voter).json()
    assert v2["you_voted"] is False and v2["votes"] == 0


def test_cannot_vote_own_reasoning(client, make_user, daily):
    author, _ = make_user("Selfie")
    r = client.post(
        "/api/picks",
        headers=author,
        json={"situation_id": daily["id"], "choice": "b", "reasoning": "My take."},
    )
    # find the author's own post
    arena = client.get("/api/debate/current").json()
    sit = next(s for s in arena["situations"] if s["situation_id"] == daily["id"])
    mine = next(p for p in sit["posts"] if p["author"] == "Selfie")
    bad = client.post(f"/api/debate/posts/{mine['pick_id']}/vote", headers=author)
    assert bad.status_code == 400


def test_vote_requires_auth(client, make_user, daily):
    author, _ = make_user("NeedsAuth")
    client.post(
        "/api/picks",
        headers=author,
        json={"situation_id": daily["id"], "choice": "a", "reasoning": "x"},
    )
    arena = client.get("/api/debate/current").json()
    sit = next(s for s in arena["situations"] if s["situation_id"] == daily["id"])
    pid = sit["posts"][0]["pick_id"]
    assert client.post(f"/api/debate/posts/{pid}/vote").status_code == 401
