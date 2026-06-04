from tests.conftest import login_user, register_user


def test_house_message_creates_basic_landlord_auto_reply(client):
    register_user(client, "agent_landlord", role="landlord")
    register_user(client, "agent_tenant", role="tenant")
    landlord_headers = login_user(client, "agent_landlord")
    tenant_headers = login_user(client, "agent_tenant")

    house = client.post(
        "/api/houses",
        json={
            "title": "Agent house",
            "city": "Hangzhou",
            "district": "Xihu",
            "community": "Auto Garden",
            "address_detail": "No. 18",
            "layout": "2R1L",
            "area": 80,
            "rent": 4800,
            "deposit": 4800,
            "status": "available",
        },
        headers=landlord_headers,
    ).get_json()["data"]

    landlord = client.get("/api/auth/me", headers=landlord_headers).get_json()["data"]
    response = client.post(
        "/api/messages",
        json={
            "receiver_id": landlord["id"],
            "house_id": house["id"],
            "content": "Can I visit this house?",
        },
        headers=tenant_headers,
    )

    assert response.status_code == 201
    auto_reply = response.get_json()["data"]["auto_reply"]
    assert auto_reply["is_mine"] is False
    assert "Agent house" in auto_reply["content"]
    assert "4800" in auto_reply["content"]

    messages = client.get(
        f"/api/messages?counterpart_id={landlord['id']}&house_id={house['id']}",
        headers=tenant_headers,
    ).get_json()["data"]["items"]
    assert len(messages) == 2
    assert messages[-1]["content"] == auto_reply["content"]
