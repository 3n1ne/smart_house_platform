from datetime import timedelta
from secrets import randbelow

from flask import Blueprint, current_app, request
from flask_jwt_extended import create_access_token, jwt_required
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.base import utc_now
from app.models.role import Role
from app.models.user import User
from app.schemas.user import serialize_user
from app.utils.api_response import error_response, success_response
from app.utils.auth import get_current_user
from app.utils.operation_log import log_operation
from app.utils.sensitive import encrypt_sensitive


auth_bp = Blueprint("auth", __name__)
_verification_codes = {}


def _find_user_by_login(login_value):
    return User.query.filter(
        or_(
            User.username == login_value,
            User.email == login_value,
            User.phone == login_value,
        )
    ).first()


def _verification_key(user):
    return f"login:{user.id}"


def _verification_ttl():
    return int(current_app.config.get("MFA_CODE_TTL_SECONDS", 300))


def _issue_verification_code(user):
    code = f"{randbelow(1000000):06d}"
    expires_at = utc_now() + timedelta(seconds=_verification_ttl())
    _verification_codes[_verification_key(user)] = {
        "code_hash": generate_password_hash(code),
        "expires_at": expires_at,
        "attempts": 0,
    }
    return code, expires_at


def _verify_dynamic_code(user, code):
    record = _verification_codes.get(_verification_key(user))
    if not record or not code:
        return False
    if record["expires_at"] < utc_now():
        _verification_codes.pop(_verification_key(user), None)
        return False
    if record["attempts"] >= 5:
        _verification_codes.pop(_verification_key(user), None)
        return False

    record["attempts"] += 1
    if not check_password_hash(record["code_hash"], code):
        return False

    _verification_codes.pop(_verification_key(user), None)
    return True


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

    duplicate_fields = []
    if User.query.filter_by(username=payload["username"]).first():
        duplicate_fields.append("username")
    if payload.get("email") and User.query.filter_by(email=payload["email"]).first():
        duplicate_fields.append("email")
    if payload.get("phone") and User.query.filter_by(phone=payload["phone"]).first():
        duplicate_fields.append("phone")

    if duplicate_fields:
        return error_response(
            "duplicate resource",
            code=4009,
            status=409,
            errors={"fields": duplicate_fields},
        )

    user = User(
        role_id=role.id,
        username=payload["username"],
        email=payload.get("email"),
        phone=payload.get("phone"),
        password_hash=generate_password_hash(payload["password"]),
        real_name=payload.get("real_name"),
        identity_no=encrypt_sensitive(payload.get("identity_no")),
        is_mfa_enabled=bool(payload.get("enable_mfa") or payload.get("is_mfa_enabled")),
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


@auth_bp.post("/verification-code")
def issue_verification_code():
    payload = request.get_json(silent=True) or {}
    login_value = payload.get("username")
    if not login_value:
        return error_response(
            "validation error",
            code=4001,
            errors={"username": ["username, email or phone is required"]},
        )

    user = _find_user_by_login(login_value)
    response_data = {
        "expires_in": _verification_ttl(),
        "delivery": "response" if current_app.config.get("MFA_CODE_VISIBLE") else "configured-channel",
    }

    if user and user.status == "active":
        code, expires_at = _issue_verification_code(user)
        response_data["expires_at"] = expires_at.isoformat()
        if current_app.config.get("MFA_CODE_VISIBLE"):
            response_data["verification_code"] = code

        log_operation(
            "auth",
            "issue_verification_code",
            target_type="user",
            target_id=user.id,
            detail={"username": user.username},
            operator_id=user.id,
        )
        db.session.commit()

    return success_response(response_data, message="verification code issued")


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

    user = _find_user_by_login(login_value)
    if user is None or not check_password_hash(user.password_hash, password):
        return error_response("authentication failed", code=4002, status=401)

    if user.status != "active":
        return error_response("user is disabled", code=4003, status=403)

    mfa_required = user.is_mfa_enabled or current_app.config.get("MFA_REQUIRED", False)
    if mfa_required and not _verify_dynamic_code(user, payload.get("verification_code")):
        return error_response(
            "verification code required",
            code=4010,
            status=401,
            errors={"verification_code": ["valid dynamic verification code is required"]},
        )

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
            "user": serialize_user(user, include_private=True),
        }
    )


@auth_bp.get("/me")
@jwt_required()
def me():
    user = get_current_user()
    if user is None:
        return error_response("resource not found", code=4004, status=404)
    return success_response(serialize_user(user, include_private=True))


@auth_bp.post("/logout")
@jwt_required()
def logout():
    return success_response(message="logout success")
