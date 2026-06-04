from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.role import Role
from app.models.user import User


DEFAULT_ROLES = [
    {"code": "admin", "name": "Administrator", "description": "System administrator"},
    {"code": "landlord", "name": "Landlord", "description": "House owner"},
    {"code": "tenant", "name": "Tenant", "description": "House renter"},
]


def seed_roles():
    existing_codes = {role.code for role in Role.query.all()}
    missing_roles = [
        Role(**role_data)
        for role_data in DEFAULT_ROLES
        if role_data["code"] not in existing_codes
    ]

    if not missing_roles:
        return

    db.session.add_all(missing_roles)
    db.session.commit()


def _env_bool(value):
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _normalize_optional(value):
    value = (value or "").strip()
    return value or None


def bootstrap_admin(
    username,
    password=None,
    email=None,
    phone=None,
    real_name=None,
    reset_password=False,
):
    username = (username or "").strip()
    if not username:
        raise ValueError("ADMIN_USERNAME is required")

    seed_roles()
    admin_role = Role.query.filter_by(code="admin").first()
    if admin_role is None:
        raise ValueError("admin role is not available")

    email = _normalize_optional(email)
    phone = _normalize_optional(phone)
    real_name = _normalize_optional(real_name)
    user = User.query.filter_by(username=username).first()

    if email:
        duplicate_email_user = User.query.filter(
            User.email == email,
            User.username != username,
        ).first()
        if duplicate_email_user:
            raise ValueError("ADMIN_EMAIL is already used by another user")
    if phone:
        duplicate_phone_user = User.query.filter(
            User.phone == phone,
            User.username != username,
        ).first()
        if duplicate_phone_user:
            raise ValueError("ADMIN_PHONE is already used by another user")

    if user is None:
        if not password:
            raise ValueError("ADMIN_PASSWORD is required when creating an admin user")
        user = User(
            role_id=admin_role.id,
            username=username,
            password_hash=generate_password_hash(password),
            email=email,
            phone=phone,
            real_name=real_name,
            status="active",
        )
        db.session.add(user)
        db.session.commit()
        return {"user": user, "created": True, "password_updated": True}

    if user.role_id != admin_role.id:
        raise ValueError("ADMIN_USERNAME belongs to a non-admin user")

    user.email = email if email is not None else user.email
    user.phone = phone if phone is not None else user.phone
    user.real_name = real_name if real_name is not None else user.real_name
    user.status = "active"

    password_updated = False
    if reset_password:
        if not password:
            raise ValueError("ADMIN_PASSWORD is required when resetting admin password")
        user.password_hash = generate_password_hash(password)
        password_updated = True

    db.session.commit()
    return {"user": user, "created": False, "password_updated": password_updated}


def bootstrap_admin_from_env(env):
    return bootstrap_admin(
        username=env.get("ADMIN_USERNAME"),
        password=env.get("ADMIN_PASSWORD"),
        email=env.get("ADMIN_EMAIL"),
        phone=env.get("ADMIN_PHONE"),
        real_name=env.get("ADMIN_REAL_NAME"),
        reset_password=_env_bool(env.get("ADMIN_RESET_PASSWORD")),
    )
