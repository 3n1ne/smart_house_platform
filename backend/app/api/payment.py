from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from app.extensions import db
from app.models.base import utc_now
from app.models.payment import Payment
from app.schemas.payment import serialize_payment
from app.utils.api_response import error_response, success_response
from app.utils.auth import get_current_user, roles_required
from app.utils.operation_log import log_operation


payment_bp = Blueprint("payment", __name__)


def _get_payment_or_404(payment_id):
    payment = db.session.get(Payment, payment_id)
    if payment is None:
        return None, error_response("resource not found", code=4004, status=404)
    return payment, None


@payment_bp.get("/mine")
@roles_required("tenant", "landlord", "admin")
def list_my_payments():
    user = get_current_user()
    role = get_jwt().get("role")

    query = Payment.query
    if role == "tenant":
        query = query.filter(Payment.payer_id == user.id)
    elif role == "landlord":
        query = query.filter(Payment.payee_id == user.id)

    status = request.args.get("status")
    contract_id = request.args.get("contract_id")
    payment_type = request.args.get("payment_type")

    if status:
        query = query.filter(Payment.status == status)
    if contract_id:
        query = query.filter(Payment.contract_id == int(contract_id))
    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)

    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 50)
    pagination = query.order_by(Payment.created_at.desc()).paginate(
        page=page,
        per_page=page_size,
    )

    return success_response(
        {
            "items": [serialize_payment(item) for item in pagination.items],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": pagination.total,
            },
        }
    )


@payment_bp.patch("/<int:payment_id>/pay")
@roles_required("tenant", "admin")
def pay_payment(payment_id):
    user = get_current_user()
    role = get_jwt().get("role")
    payment, error = _get_payment_or_404(payment_id)
    if error:
        return error

    if role == "tenant" and payment.payer_id != user.id:
        return error_response("permission denied", code=4003, status=403)
    if payment.status not in {"pending", "overdue"}:
        return error_response(
            "validation error",
            code=4001,
            errors={"payment": ["only pending or overdue payments can be paid"]},
        )

    payload = request.get_json(silent=True) or {}
    payment_method = payload.get("payment_method")
    if not payment_method:
        return error_response(
            "validation error",
            code=4001,
            errors={"payment_method": ["payment_method is required"]},
        )

    payment.status = "paid"
    payment.payment_method = payment_method
    payment.transaction_no = payload.get("transaction_no")
    payment.paid_at = utc_now()
    log_operation(
        "payment",
        "pay",
        target_type="payment",
        target_id=payment.id,
        detail={"payment_method": payment_method, "amount": payment.amount},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(
        serialize_payment(payment),
        message="payment completed",
    )
