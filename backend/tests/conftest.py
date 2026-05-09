import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app(tmp_path):
    flask_app = create_app(
        "testing",
        {
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        },
    )

    yield flask_app

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register_user(client, username, role="tenant", password="password123", **extra):
    payload = {
        "role": role,
        "username": username,
        "password": password,
        **extra,
    }
    return client.post("/api/auth/register", json=payload)


def login_user(client, username, password="password123"):
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    token = response.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
