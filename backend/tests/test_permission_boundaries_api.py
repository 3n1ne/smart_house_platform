from tests.conftest import login_user, register_user


def _house_payload(**overrides):
    payload = {
        "title": "权限测试房源",
        "city": "南京",
        "district": "鼓楼区",
        "address_detail": "中山路 1 号",
        "layout": "2室1厅",
        "area": 75,
        "rent": 5200,
        "deposit": 5200,
        "status": "available",
    }
    payload.update(overrides)
    return payload


def test_landlord_cannot_manage_another_landlords_house(client):
    register_user(client, "owner_landlord", role="landlord")
    register_user(client, "other_landlord", role="landlord")
    owner_headers = login_user(client, "owner_landlord")
    other_headers = login_user(client, "other_landlord")

    created = client.post("/api/houses", json=_house_payload(), headers=owner_headers)
    assert created.status_code == 201
    house_id = created.get_json()["data"]["id"]

    update_response = client.put(
        f"/api/houses/{house_id}",
        json={"title": "越权修改"},
        headers=other_headers,
    )
    status_response = client.patch(
        f"/api/houses/{house_id}/status",
        json={"status": "offline"},
        headers=other_headers,
    )
    delete_response = client.delete(f"/api/houses/{house_id}", headers=other_headers)

    assert update_response.status_code == 403
    assert status_response.status_code == 403
    assert delete_response.status_code == 403


def test_landlord_cannot_manage_another_landlords_news(client):
    register_user(client, "news_owner", role="landlord")
    register_user(client, "news_other", role="landlord")
    owner_headers = login_user(client, "news_owner")
    other_headers = login_user(client, "news_other")

    created = client.post(
        "/api/news",
        json={"title": "业主公告", "content": "公共设施维护", "status": "draft"},
        headers=owner_headers,
    )
    assert created.status_code == 201
    news_id = created.get_json()["data"]["id"]

    update_response = client.put(
        f"/api/news/{news_id}",
        json={"title": "越权公告"},
        headers=other_headers,
    )
    status_response = client.patch(
        f"/api/news/{news_id}/status",
        json={"status": "published"},
        headers=other_headers,
    )
    delete_response = client.delete(f"/api/news/{news_id}", headers=other_headers)

    assert update_response.status_code == 403
    assert status_response.status_code == 403
    assert delete_response.status_code == 403


def test_non_admin_cannot_manage_users(client):
    register_user(client, "user_tenant", role="tenant")
    register_user(client, "user_landlord", role="landlord")
    tenant_headers = login_user(client, "user_tenant")
    landlord_headers = login_user(client, "user_landlord")

    list_response = client.get("/api/users", headers=tenant_headers)
    status_response = client.patch(
        "/api/users/1/status",
        json={"status": "disabled"},
        headers=landlord_headers,
    )

    assert list_response.status_code == 403
    assert status_response.status_code == 403


def test_house_scoped_message_must_involve_house_landlord(client):
    register_user(client, "message_landlord", role="landlord")
    register_user(client, "message_tenant_a", role="tenant")
    register_user(client, "message_tenant_b", role="tenant")
    landlord_headers = login_user(client, "message_landlord")
    tenant_headers = login_user(client, "message_tenant_a")

    created_house = client.post("/api/houses", json=_house_payload(), headers=landlord_headers)
    assert created_house.status_code == 201
    house_id = created_house.get_json()["data"]["id"]

    tenant_b_login = client.post(
        "/api/auth/login",
        json={"username": "message_tenant_b", "password": "password123"},
    )
    receiver_id = tenant_b_login.get_json()["data"]["user"]["id"]

    response = client.post(
        "/api/messages",
        json={"receiver_id": receiver_id, "house_id": house_id, "content": "这套房如何？"},
        headers=tenant_headers,
    )

    assert response.status_code == 400
    assert response.get_json()["code"] == 4001
