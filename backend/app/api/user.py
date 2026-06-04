from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from app.extensions import db
from app.models.booking import Booking
from app.models.complaint import Complaint
from app.models.contract import Contract
from app.models.payment import Payment
from app.models.repair import Repair
from app.models.user import User
from app.schemas.booking import serialize_booking
from app.schemas.complaint import serialize_complaint
from app.schemas.contract import serialize_contract
from app.schemas.payment import serialize_payment
from app.schemas.repair import serialize_repair
from app.schemas.user import serialize_user
from app.utils.api_response import error_response, success_response
from app.utils.auth import get_current_user, roles_required
from app.utils.operation_log import log_operation
from app.utils.sensitive import encrypt_sensitive


user_bp = Blueprint("user", __name__)


def _limit(query, model, limit=5):
    return query.order_by(model.created_at.desc(), model.id.desc()).limit(limit).all()


@user_bp.get("/profile")
@jwt_required()
def get_profile():
    user = get_current_user()
    if user is None:
        return error_response("resource not found", code=4004, status=404)
    return success_response(serialize_user(user, include_private=True))


@user_bp.put("/profile")
@jwt_required()
def update_profile():
    user = get_current_user()
    if user is None:
        return error_response("resource not found", code=4004, status=404)

    payload = request.get_json(silent=True) or {}
    allowed_fields = [
        "real_name",
        "email",
        "phone",
        "avatar_url",
        "gender",
        "identity_no",
        "is_mfa_enabled",
    ]

    for field in allowed_fields:
        if field in payload:
            if field == "is_mfa_enabled":
                setattr(user, field, bool(payload[field]))
            elif field == "identity_no":
                setattr(user, field, encrypt_sensitive(payload[field]))
            else:
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
    return success_response(serialize_user(user, include_private=True), message="profile updated")


@user_bp.get("/rental-history")
@jwt_required()
def rental_history():
    user = get_current_user()
    if user is None:
        return error_response("resource not found", code=4004, status=404)

    role = user.role.code if user.role else None
    if role == "tenant":
        booking_query = Booking.query.filter(Booking.tenant_id == user.id)
        contract_query = Contract.query.filter(Contract.tenant_id == user.id)
        payment_query = Payment.query.filter(Payment.payer_id == user.id)
        repair_query = Repair.query.filter(Repair.tenant_id == user.id)
        complaint_query = Complaint.query.filter(Complaint.complainant_id == user.id)
    elif role == "landlord":
        booking_query = Booking.query.filter(Booking.landlord_id == user.id)
        contract_query = Contract.query.filter(Contract.landlord_id == user.id)
        payment_query = Payment.query.filter(Payment.payee_id == user.id)
        repair_query = Repair.query.join(Repair.house).filter_by(landlord_id=user.id)
        complaint_query = Complaint.query.join(Complaint.house).filter_by(landlord_id=user.id)
    else:
        booking_query = Booking.query
        contract_query = Contract.query
        payment_query = Payment.query
        repair_query = Repair.query
        complaint_query = Complaint.query

    contracts = _limit(contract_query, Contract, 8)
    payments = _limit(payment_query, Payment, 8)
    bookings = _limit(booking_query, Booking, 8)
    repairs = _limit(repair_query, Repair, 8)
    complaints = _limit(complaint_query, Complaint, 8)

    return success_response(
        {
            "summary": {
                "bookings": booking_query.count(),
                "contracts": contract_query.count(),
                "payments": payment_query.count(),
                "repairs": repair_query.count(),
                "complaints": complaint_query.count(),
            },
            "recent_bookings": [serialize_booking(item) for item in bookings],
            "recent_contracts": [serialize_contract(item) for item in contracts],
            "recent_payments": [serialize_payment(item) for item in payments],
            "recent_repairs": [serialize_repair(item) for item in repairs],
            "recent_complaints": [serialize_complaint(item) for item in complaints],
        }
    )


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
