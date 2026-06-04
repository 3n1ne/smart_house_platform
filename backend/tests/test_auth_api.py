from tests.conftest import login_user, register_user


def test_register_login_and_me(client):
    response = register_user(
        client,
        "tenant_001",
        role="tenant",
        email="tenant001@example.com",
        phone="13800000001",
        real_name="Tenant One",
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["code"] == 0
    assert body["data"]["role"] == "tenant"

    duplicate = register_user(client, "tenant_001", role="tenant")
    assert duplicate.status_code == 409
    duplicate_body = duplicate.get_json()
    assert duplicate_body["code"] == 4009
    assert duplicate_body["errors"]["fields"] == ["username"]

    headers = login_user(client, "tenant_001")
    me = client.get("/api/auth/me", headers=headers)

    assert me.status_code == 200
    assert me.get_json()["data"]["username"] == "tenant_001"


def test_register_rejects_invalid_role(client):
    response = register_user(client, "admin_attempt", role="admin")

    assert response.status_code == 400
    assert response.get_json()["code"] == 4001
