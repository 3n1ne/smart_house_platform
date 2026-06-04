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


def _can_access_payment(user, role, payment):
    if role == "admin":
        return True
    if role == "tenant":
        return payment.payer_id == user.id
    if role == "landlord":
        return payment.payee_id == user.id
    return False


def _transaction_no(payment):
    return f"PAY{utc_now().strftime('%Y%m%d%H%M%S')}{payment.id}"


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
    payment.transaction_no = payload.get("transaction_no") or _transaction_no(payment)
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


@payment_bp.patch("/<int:payment_id>/fail")
@roles_required("tenant", "admin")
def fail_payment(payment_id):
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
            errors={"payment": ["only pending or overdue payments can be marked failed"]},
        )

    payload = request.get_json(silent=True) or {}
    payment.status = "failed"
    payment.payment_method = payload.get("payment_method", payment.payment_method)
    log_operation(
        "payment",
        "fail",
        target_type="payment",
        target_id=payment.id,
        detail={"reason": payload.get("reason")},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(serialize_payment(payment), message="payment failed")


@payment_bp.patch("/<int:payment_id>/refund")
@roles_required("landlord", "admin")
def refund_payment(payment_id):
    user = get_current_user()
    role = get_jwt().get("role")
    payment, error = _get_payment_or_404(payment_id)
    if error:
        return error

    if role == "landlord" and payment.payee_id != user.id:
        return error_response("permission denied", code=4003, status=403)
    if payment.status != "paid":
        return error_response(
            "validation error",
            code=4001,
            errors={"payment": ["only paid payments can be refunded"]},
        )

    payload = request.get_json(silent=True) or {}
    payment.status = "refunded"
    log_operation(
        "payment",
        "refund",
        target_type="payment",
        target_id=payment.id,
        detail={"reason": payload.get("reason"), "transaction_no": payment.transaction_no},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(serialize_payment(payment), message="payment refunded")


@payment_bp.post("/overdue-scan")
@roles_required("landlord", "admin")
def mark_overdue_payments():
    user = get_current_user()
    role = get_jwt().get("role")
    today = utc_now().date()

    query = Payment.query.filter(Payment.status == "pending", Payment.due_date < today)
    if role == "landlord":
        query = query.filter(Payment.payee_id == user.id)

    payments = query.all()
    for payment in payments:
        payment.status = "overdue"
        log_operation(
            "payment",
            "mark_overdue",
            target_type="payment",
            target_id=payment.id,
            detail={"due_date": payment.due_date.isoformat() if payment.due_date else None},
            operator_id=user.id,
        )

    db.session.commit()
    return success_response(
        {
            "updated_count": len(payments),
            "items": [serialize_payment(payment) for payment in payments],
        },
        message="overdue payments updated",
    )
