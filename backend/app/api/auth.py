from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.role import Role
from app.models.user import User
from app.models.base import utc_now
from app.schemas.user import serialize_user
from app.utils.api_response import error_response, success_response
from app.utils.auth import get_current_user
from app.utils.operation_log import log_operation


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}

    required_fields = ["role", "username", "password"]
    missing_fields = [field for field in required_fields if not payload.get(field)]
    if missing_fields:
        return error_response(
            "validation error",
            code=4001,
            errors={"missing_fields": missing_fields},
        )

    if payload["role"] not in {"landlord", "tenant"}:
        return error_response(
            "validation error",
            code=4001,
            errors={"role": ["role must be landlord or tenant"]},
        )

    role = Role.query.filter_by(code=payload["role"]).first()
    if role is None:
        return error_response("role not found", code=4004, status=404)

    duplicate_conditions = [User.username == payload["username"]]
    if payload.get("email"):
        duplicate_conditions.append(User.email == payload["email"])
    if payload.get("phone"):
        duplicate_conditions.append(User.phone == payload["phone"])

    duplicate_user = User.query.filter(or_(*duplicate_conditions)).first()
    if duplicate_user:
        return error_response("duplicate resource", code=4009, status=409)

    user = User(
        role_id=role.id,
        username=payload["username"],
        email=payload.get("email"),
        phone=payload.get("phone"),
        password_hash=generate_password_hash(payload["password"]),
        real_name=payload.get("real_name"),
        status="active",
    )
    db.session.add(user)
    db.session.flush()
    log_operation(
        "auth",
        "register",
        target_type="user",
        target_id=user.id,
        detail={"role": role.code, "username": user.username},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(
        {
            "user_id": user.id,
            "username": user.username,
            "role": role.code,
        },
        message="register success",
        status=201,
    )


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    login_value = payload.get("username")
    password = payload.get("password")

    if not login_value or not password:
        return error_response(
            "validation error",
            code=4001,
            errors={"credentials": ["username and password are required"]},
        )

    user = User.query.filter(
        or_(
            User.username == login_value,
            User.email == login_value,
            User.phone == login_value,
        )
    ).first()
    if user is None or not check_password_hash(user.password_hash, password):
        return error_response("authentication failed", code=4002, status=401)

    if user.status != "active":
        return error_response("user is disabled", code=4003, status=403)

    user.last_login_at = utc_now()
    log_operation(
        "auth",
        "login",
        target_type="user",
        target_id=user.id,
        detail={"username": user.username},
        operator_id=user.id,
    )
    db.session.commit()

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role.code if user.role else None,
            "username": user.username,
        },
    )

    return success_response(
        {
            "access_token": access_token,
            "token_type": "Bearer",
            "user": serialize_user(user),
        }
    )


@auth_bp.get("/me")
@jwt_required()
def me():
    user = get_current_user()
    if user is None:
        return error_response("resource not found", code=4004, status=404)
    return success_response(serialize_user(user))


@auth_bp.post("/logout")
@jwt_required()
def logout():
    return success_response(message="logout success")
