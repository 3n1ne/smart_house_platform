from datetime import date
from uuid import uuid4

from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from app.extensions import db
from app.models.base import utc_now
from app.models.booking import Booking
from app.models.contract import Contract
from app.models.house import House
from app.models.payment import Payment
from app.schemas.contract import serialize_contract
from app.utils.api_response import error_response, success_response
from app.utils.auth import get_current_user, roles_required
from app.utils.operation_log import log_operation


contract_bp = Blueprint("contract", __name__)


def _generate_contract_no():
    return f"CTR{utc_now():%Y%m%d%H%M%S}{uuid4().hex[:6].upper()}"


def _parse_date(value, field_name):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid YYYY-MM-DD date")


def _get_contract_or_404(contract_id):
    contract = db.session.get(Contract, contract_id)
    if contract is None:
        return None, error_response("resource not found", code=4004, status=404)
    return contract, None


def _create_initial_payments(contract):
    existing_count = Payment.query.filter_by(contract_id=contract.id).count()
    if existing_count:
        return

    db.session.add(
        Payment(
            contract_id=contract.id,
            payer_id=contract.tenant_id,
            payee_id=contract.landlord_id,
            amount=contract.monthly_rent,
            payment_type="rent",
            due_date=contract.start_date,
            status="pending",
        )
    )


@contract_bp.post("")
@roles_required("landlord", "admin")
def create_contract():
    user = get_current_user()
    role = get_jwt().get("role")
    payload = request.get_json(silent=True) or {}

    booking_id = payload.get("booking_id")
    if not booking_id:
        return error_response(
            "validation error",
            code=4001,
            errors={"booking_id": ["booking_id is required"]},
        )

    booking = db.session.get(Booking, int(booking_id))
    if booking is None:
        return error_response("resource not found", code=4004, status=404)
    if role == "landlord" and booking.landlord_id != user.id:
        return error_response("permission denied", code=4003, status=403)
    if booking.status not in {"confirmed", "completed"}:
        return error_response(
            "validation error",
            code=4001,
            errors={"booking": ["booking must be confirmed or completed"]},
        )

    try:
        start_date = _parse_date(payload.get("start_date"), "start_date")
        end_date = _parse_date(payload.get("end_date"), "end_date")
    except ValueError as exc:
        return error_response(
            "validation error",
            code=4001,
            errors={"date": [str(exc)]},
        )

    if start_date >= end_date:
        return error_response(
            "validation error",
            code=4001,
            errors={"date": ["end_date must be later than start_date"]},
        )

    duplicate_contract = (
        Contract.query.filter_by(
            house_id=booking.house_id,
            landlord_id=booking.landlord_id,
            tenant_id=booking.tenant_id,
        )
        .filter(Contract.status.in_(["draft", "signed", "active"]))
        .first()
    )
    if duplicate_contract:
        return error_response("duplicate resource", code=4009, status=409)

    house = db.session.get(House, booking.house_id)
    contract = Contract(
        contract_no=_generate_contract_no(),
        house_id=booking.house_id,
        landlord_id=booking.landlord_id,
        tenant_id=booking.tenant_id,
        start_date=start_date,
        end_date=end_date,
        monthly_rent=house.rent,
        deposit=house.deposit,
        payment_cycle=payload.get("payment_cycle") or "monthly",
        status="draft",
        content=payload.get("content"),
    )
    db.session.add(contract)
    db.session.flush()
    log_operation(
        "contract",
        "create",
        target_type="contract",
        target_id=contract.id,
        detail={"booking_id": booking.id, "contract_no": contract.contract_no},
        operator_id=user.id if user else None,
    )
    db.session.commit()

    return success_response(
        serialize_contract(contract),
        message="contract created",
        status=201,
    )


@contract_bp.get("/mine")
@roles_required("tenant", "landlord", "admin")
def list_my_contracts():
    user = get_current_user()
    role = get_jwt().get("role")

    query = Contract.query
    if role == "tenant":
        query = query.filter(Contract.tenant_id == user.id)
    elif role == "landlord":
        query = query.filter(Contract.landlord_id == user.id)

    status = request.args.get("status")
    house_id = request.args.get("house_id")
    if status:
        query = query.filter(Contract.status == status)
    if house_id:
        query = query.filter(Contract.house_id == int(house_id))

    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 50)
    pagination = query.order_by(Contract.created_at.desc()).paginate(
        page=page,
        per_page=page_size,
    )

    return success_response(
        {
            "items": [serialize_contract(item) for item in pagination.items],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": pagination.total,
            },
        }
    )


@contract_bp.patch("/<int:contract_id>/sign")
@roles_required("tenant", "admin")
def sign_contract(contract_id):
    user = get_current_user()
    role = get_jwt().get("role")
    contract, error = _get_contract_or_404(contract_id)
    if error:
        return error

    if role == "tenant" and contract.tenant_id != user.id:
        return error_response("permission denied", code=4003, status=403)
    if contract.status != "draft":
        return error_response(
            "validation error",
            code=4001,
            errors={"contract": ["only draft contracts can be signed"]},
        )

    contract.status = "active"
    contract.signed_at = utc_now()
    contract.house.status = "rented"

    related_booking = (
        Booking.query.filter_by(
            house_id=contract.house_id,
            tenant_id=contract.tenant_id,
            landlord_id=contract.landlord_id,
        )
        .filter(Booking.status.in_(["confirmed", "pending"]))
        .order_by(Booking.created_at.desc())
        .first()
    )
    if related_booking:
        related_booking.status = "completed"

    _create_initial_payments(contract)
    log_operation(
        "contract",
        "sign",
        target_type="contract",
        target_id=contract.id,
        detail={"contract_no": contract.contract_no},
        operator_id=user.id if user else None,
    )
    db.session.commit()

    return success_response(
        serialize_contract(contract),
        message="contract signed",
    )


@contract_bp.patch("/<int:contract_id>/status")
@roles_required("landlord", "admin")
def update_contract_status(contract_id):
    user = get_current_user()
    role = get_jwt().get("role")
    contract, error = _get_contract_or_404(contract_id)
    if error:
        return error

    if role == "landlord" and contract.landlord_id != user.id:
        return error_response("permission denied", code=4003, status=403)

    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    if status not in {"terminated", "expired"}:
        return error_response(
            "validation error",
            code=4001,
            errors={"status": ["status must be terminated or expired"]},
        )
    if contract.status not in {"active", "signed"}:
        return error_response(
            "validation error",
            code=4001,
            errors={"contract": ["only active contracts can change to ended states"]},
        )

    contract.status = status
    if contract.house.status == "rented":
        contract.house.status = "available"
    log_operation(
        "contract",
        "update_status",
        target_type="contract",
        target_id=contract.id,
        detail={"status": status, "contract_no": contract.contract_no},
        operator_id=user.id if user else None,
    )
    db.session.commit()

    return success_response(
        serialize_contract(contract),
        message="contract status updated",
    )
