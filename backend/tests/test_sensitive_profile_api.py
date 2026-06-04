from app.extensions import db
from app.models.role import Role
from app.models.user import User
from tests.conftest import login_user, register_user


def test_identity_number_is_encrypted_at_rest_and_masked_in_profile(client, app):
    register_user(client, "sensitive_tenant", role="tenant")
    headers = login_user(client, "sensitive_tenant")

    response = client.put(
        "/api/users/profile",
        json={"identity_no": "330102199001012222"},
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["identity_no_masked"] == "33************2222"
    assert "330102199001012222" not in str(payload)

    with app.app_context():
        user = User.query.filter_by(username="sensitive_tenant").first()
        assert user.identity_no.startswith("enc:v1:")
        assert user.identity_no != "330102199001012222"


def test_admin_user_list_masks_contact_fields(client):
    register_user(
        client,
        "masked_tenant",
        role="tenant",
        email="masked@example.com",
        phone="13800000002",
    )
    admin = register_user(client, "masked_admin_seed", role="tenant")
    assert admin.status_code == 201

    with client.application.app_context():
        user = User.query.filter_by(username="masked_admin_seed").first()
        admin_role = Role.query.filter_by(code="admin").one()
        user.role_id = admin_role.id
        db.session.commit()

    headers = login_user(client, "masked_admin_seed")
    response = client.get("/api/users?keyword=masked", headers=headers)

    assert response.status_code == 200
    items = response.get_json()["data"]["items"]
    tenant = next(item for item in items if item["username"] == "masked_tenant")
    assert tenant["phone"] == "138****0002"
    assert tenant["email"] == "ma***@example.com"
