from tests.conftest import register_user


def test_mfa_enabled_user_must_login_with_dynamic_verification_code(client):
    register_response = register_user(
        client,
        "mfa_tenant",
        role="tenant",
        password="password123",
        enable_mfa=True,
    )
    assert register_response.status_code == 201

    missing_code = client.post(
        "/api/auth/login",
        json={"username": "mfa_tenant", "password": "password123"},
    )
    assert missing_code.status_code == 401
    assert missing_code.get_json()["code"] == 4010

    code_response = client.post(
        "/api/auth/verification-code",
        json={"username": "mfa_tenant"},
    )
    assert code_response.status_code == 200
    verification_code = code_response.get_json()["data"]["verification_code"]

    bad_code = client.post(
        "/api/auth/login",
        json={
            "username": "mfa_tenant",
            "password": "password123",
            "verification_code": "000000",
        },
    )
    assert bad_code.status_code == 401

    success = client.post(
        "/api/auth/login",
        json={
            "username": "mfa_tenant",
            "password": "password123",
            "verification_code": verification_code,
        },
    )
    assert success.status_code == 200
    assert success.get_json()["data"]["user"]["is_mfa_enabled"] is True
