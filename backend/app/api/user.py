from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from app.extensions import db
from app.models.user import User
from app.schemas.user import serialize_user
from app.utils.api_response import error_response, success_response
from app.utils.auth import get_current_user, roles_required
from app.utils.operation_log import log_operation


user_bp = Blueprint("user", __name__)


@user_bp.get("/profile")
@jwt_required()
def get_profile():
    user = get_current_user()
    if user is None:
        return error_response("resource not found", code=4004, status=404)
    return success_response(serialize_user(user))


@user_bp.put("/profile")
@jwt_required()
def update_profile():
    user = get_current_user()
    if user is None:
        return error_response("resource not found", code=4004, status=404)

    payload = request.get_json(silent=True) or {}
    allowed_fields = ["real_name", "email", "phone", "avatar_url", "gender"]

    for field in allowed_fields:
        if field in payload:
            setattr(user, field, payload[field])

    log_operation(
        "user",
        "update_profile",
        target_type="user",
        target_id=user.id,
        detail={"fields": [field for field in allowed_fields if field in payload]},
        operator_id=user.id,
    )
    db.session.commit()
    return success_response(serialize_user(user), message="profile updated")


@user_bp.get("")
@roles_required("admin")
def list_users():
    query = User.query

    role = request.args.get("role")
    status = request.args.get("status")
    keyword = request.args.get("keyword")

    if role:
        query = query.join(User.role).filter_by(code=role)
    if status:
        query = query.filter(User.status == status)
    if keyword:
        like_value = f"%{keyword}%"
        query = query.filter(
            or_(
                User.username.like(like_value),
                User.real_name.like(like_value),
                User.phone.like(like_value),
            )
        )

    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 50)
    pagination = query.order_by(User.id.desc()).paginate(page=page, per_page=page_size)

    return success_response(
        {
            "items": [serialize_user(user) for user in pagination.items],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": pagination.total,
            },
        }
    )


@user_bp.patch("/<int:user_id>/status")
@roles_required("admin")
def update_user_status(user_id):
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    if status not in {"active", "disabled"}:
        return error_response(
            "validation error",
            code=4001,
            errors={"status": ["status must be active or disabled"]},
        )

    user = db.session.get(User, user_id)
    if user is None:
        return error_response("resource not found", code=4004, status=404)

    user.status = status
    operator = get_current_user()
    log_operation(
        "user",
        "update_status",
        target_type="user",
        target_id=user.id,
        detail={"status": status},
        operator_id=operator.id if operator else None,
    )
    db.session.commit()
    return success_response(serialize_user(user), message="user status updated")
