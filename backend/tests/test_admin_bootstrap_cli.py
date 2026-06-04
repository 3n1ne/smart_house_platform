from app.models.user import User
from tests.conftest import register_user


def _set_admin_env(monkeypatch, **overrides):
    values = {
        "ADMIN_USERNAME": "admin_cli",
        "ADMIN_PASSWORD": "admin-password-123",
        "ADMIN_EMAIL": "admin@example.com",
        "ADMIN_PHONE": "13900000000",
        "ADMIN_REAL_NAME": "平台管理员",
        "ADMIN_RESET_PASSWORD": "",
    }
    values.update(overrides)
    for key, value in values.items():
        monkeypatch.setenv(key, value)


def test_seed_admin_creates_admin_and_allows_login(app, client, monkeypatch):
    _set_admin_env(monkeypatch)

    result = app.test_cli_runner().invoke(args=["seed-admin"])

    assert result.exit_code == 0
    assert "admin created: admin_cli" in result.output

    with app.app_context():
        user = User.query.filter_by(username="admin_cli").one()
        assert user.role.code == "admin"
        assert user.status == "active"
        assert user.email == "admin@example.com"

    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin_cli", "password": "admin-password-123"},
    )
    assert login_response.status_code == 200
    assert login_response.get_json()["data"]["user"]["role"] == "admin"


def test_seed_admin_does_not_reset_existing_password_without_flag(app, client, monkeypatch):
    _set_admin_env(monkeypatch)
    first_result = app.test_cli_runner().invoke(args=["seed-admin"])
    assert first_result.exit_code == 0

    _set_admin_env(
        monkeypatch,
        ADMIN_PASSWORD="new-admin-password-456",
        ADMIN_EMAIL="updated-admin@example.com",
    )
    second_result = app.test_cli_runner().invoke(args=["seed-admin"])

    assert second_result.exit_code == 0
    assert "admin updated: admin_cli" in second_result.output
    assert "password_updated=true" not in second_result.output

    old_password_login = client.post(
        "/api/auth/login",
        json={"username": "admin_cli", "password": "admin-password-123"},
    )
    new_password_login = client.post(
        "/api/auth/login",
        json={"username": "admin_cli", "password": "new-admin-password-456"},
    )

    assert old_password_login.status_code == 200
    assert new_password_login.status_code == 401

    with app.app_context():
        user = User.query.filter_by(username="admin_cli").one()
        assert user.email == "updated-admin@example.com"


def test_seed_admin_resets_existing_password_with_flag(app, client, monkeypatch):
    _set_admin_env(monkeypatch)
    first_result = app.test_cli_runner().invoke(args=["seed-admin"])
    assert first_result.exit_code == 0

    _set_admin_env(
        monkeypatch,
        ADMIN_PASSWORD="new-admin-password-456",
        ADMIN_RESET_PASSWORD="true",
    )
    second_result = app.test_cli_runner().invoke(args=["seed-admin"])

    assert second_result.exit_code == 0
    assert "password_updated=true" in second_result.output

    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin_cli", "password": "new-admin-password-456"},
    )
    assert login_response.status_code == 200


def test_seed_admin_rejects_existing_non_admin_username(app, client, monkeypatch):
    register_user(client, "admin_cli", role="tenant")
    _set_admin_env(monkeypatch)

    result = app.test_cli_runner().invoke(args=["seed-admin"])

    assert result.exit_code != 0
    assert "ADMIN_USERNAME belongs to a non-admin user" in result.output

    with app.app_context():
        user = User.query.filter_by(username="admin_cli").one()
        assert user.role.code == "tenant"
