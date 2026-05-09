from datetime import datetime, timezone

from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from app.extensions import db
from app.models.base import utc_now
from app.models.booking import Booking
from app.models.house import House
from app.schemas.booking import serialize_booking
from app.utils.api_response import error_response, success_response
from app.utils.auth import get_current_user, roles_required
from app.utils.operation_log import log_operation


booking_bp = Blueprint("booking", __name__)


def _get_booking_or_404(booking_id):
    booking = db.session.get(Booking, booking_id)
    if booking is None:
        return None, error_response("resource not found", code=4004, status=404)
    return booking, None


@booking_bp.post("")
@roles_required("tenant")
def create_booking():
    user = get_current_user()
    payload = request.get_json(silent=True) or {}

    house_id = payload.get("house_id")
    appointment_time = payload.get("appointment_time")

    if not house_id or not appointment_time:
        return error_response(
            "validation error",
            code=4001,
            errors={"booking": ["house_id and appointment_time are required"]},
        )

    house = db.session.get(House, int(house_id))
    if house is None:
        return error_response("resource not found", code=4004, status=404)
    if house.status != "available":
        return error_response(
            "validation error",
            code=4001,
            errors={"house": ["only available houses can be booked"]},
        )

    try:
        parsed_time = datetime.fromisoformat(appointment_time)
    except ValueError:
        return error_response(
            "validation error",
            code=4001,
            errors={"appointment_time": ["invalid ISO datetime format"]},
        )

    if parsed_time.tzinfo is not None:
        parsed_time = parsed_time.astimezone(timezone.utc).replace(tzinfo=None)

    if parsed_time <= utc_now():
        return error_response(
            "validation error",
            code=4001,
            errors={"appointment_time": ["appointment_time must be in the future"]},
        )

    booking = Booking(
        house_id=house.id,
        tenant_id=user.id,
        landlord_id=house.landlord_id,
        appointment_time=parsed_time,
        remark=payload.get("remark"),
        status="pending",
    )
    db.session.add(booking)
    db.session.flush()
    log_operation(
        "booking",
        "create",
        target_type="booking",
        target_id=booking.id,
        detail={"house_id": house.id, "appointment_time": parsed_time.isoformat()},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(
        serialize_booking(booking),
        message="booking created",
        status=201,
    )


@booking_bp.get("/mine")
@roles_required("tenant", "landlord", "admin")
def list_my_bookings():
    user = get_current_user()
    role = get_jwt().get("role")

    query = Booking.query
    if role == "tenant":
        query = query.filter(Booking.tenant_id == user.id)
    elif role == "landlord":
        query = query.filter(Booking.landlord_id == user.id)

    status = request.args.get("status")
    house_id = request.args.get("house_id")

    if status:
        query = query.filter(Booking.status == status)
    if house_id:
        query = query.filter(Booking.house_id == int(house_id))

    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 50)
    pagination = query.order_by(Booking.appointment_time.asc()).paginate(
        page=page,
        per_page=page_size,
    )

    return success_response(
        {
            "items": [serialize_booking(item) for item in pagination.items],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": pagination.total,
            },
        }
    )


@booking_bp.patch("/<int:booking_id>/status")
@roles_required("tenant", "landlord", "admin")
def update_booking_status(booking_id):
    booking, error = _get_booking_or_404(booking_id)
    if error:
        return error

    user = get_current_user()
    role = get_jwt().get("role")
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    allowed_statuses = {"confirmed", "cancelled", "completed"}

    if status not in allowed_statuses:
        return error_response(
            "validation error",
            code=4001,
            errors={"status": [f"status must be one of {sorted(allowed_statuses)}"]},
        )

    if booking.status in {"cancelled", "completed"}:
        return error_response(
            "validation error",
            code=4001,
            errors={"booking": ["booking can no longer be updated"]},
        )

    if status == "confirmed" and booking.status != "pending":
        return error_response(
            "validation error",
            code=4001,
            errors={"booking": ["only pending bookings can be confirmed"]},
        )

    if status == "completed" and booking.status != "confirmed":
        return error_response(
            "validation error",
            code=4001,
            errors={"booking": ["only confirmed bookings can be completed"]},
        )

    if role == "tenant":
        if booking.tenant_id != user.id:
            return error_response("permission denied", code=4003, status=403)
        if status != "cancelled":
            return error_response(
                "permission denied",
                code=4003,
                status=403,
            )
    elif role == "landlord":
        if booking.landlord_id != user.id:
            return error_response("permission denied", code=4003, status=403)

    booking.status = status
    if status == "confirmed":
        booking.confirmed_at = utc_now()
    log_operation(
        "booking",
        "update_status",
        target_type="booking",
        target_id=booking.id,
        detail={"status": status},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(
        serialize_booking(booking),
        message="booking status updated",
    )
