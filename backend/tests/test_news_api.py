from tests.conftest import login_user, register_user


def test_news_lifecycle_controls_public_visibility(client):
    register_user(client, "landlord_news", role="landlord")
    headers = login_user(client, "landlord_news")

    draft = client.post(
        "/api/news",
        json={"title": "停水通知", "content": "本周五上午检修。", "status": "draft"},
        headers=headers,
    )
    assert draft.status_code == 201
    news_id = draft.get_json()["data"]["id"]

    public_drafts = client.get("/api/news")
    assert public_drafts.status_code == 200
    assert public_drafts.get_json()["data"]["pagination"]["total"] == 0

    published = client.patch(
        f"/api/news/{news_id}/status",
        json={"status": "published"},
        headers=headers,
    )
    assert published.status_code == 200
    assert published.get_json()["data"]["published_at"] is not None

    public_news = client.get("/api/news?keyword=停水")
    assert public_news.status_code == 200
    body = public_news.get_json()["data"]
    assert body["pagination"]["total"] == 1
    assert body["items"][0]["title"] == "停水通知"
