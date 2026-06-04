from datetime import timedelta

from flask import Blueprint
from sqlalchemy import func

from app.extensions import db
from app.models.base import utc_now
from app.models.booking import Booking
from app.models.complaint import Complaint
from app.models.contract import Contract
from app.models.house import House
from app.models.news import News
from app.models.operation_log import OperationLog
from app.models.payment import Payment
from app.models.repair import Repair
from app.models.user import User
from app.utils.api_response import success_response
from app.utils.auth import roles_required


report_bp = Blueprint("report", __name__)


def _count_by(model, column):
    rows = db.session.query(column, func.count(model.id)).group_by(column).all()
    return {key or "unknown": count for key, count in rows}


def _rent_income_trend():
    trend = {}
    paid_payments = (
        Payment.query.filter(Payment.status == "paid", Payment.paid_at.isnot(None))
        .order_by(Payment.paid_at.asc())
        .all()
    )
    for payment in paid_payments:
        month_key = payment.paid_at.strftime("%Y-%m")
        trend[month_key] = trend.get(month_key, 0) + float(payment.amount or 0)
    return [{"month": month, "amount": amount} for month, amount in trend.items()]


@report_bp.get("/overview")
@roles_required("admin")
def overview():
    total_houses = House.query.count()
    rented_houses = House.query.filter(House.status == "rented").count()
    paid_total = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.status == "paid")
        .scalar()
    )
    pending_payment_total = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.status.in_(["pending", "overdue"]))
        .scalar()
    )
    active_since = utc_now() - timedelta(days=30)
    active_users_30d = (
        db.session.query(func.count(func.distinct(OperationLog.operator_id)))
        .filter(OperationLog.operator_id.isnot(None), OperationLog.created_at >= active_since)
        .scalar()
    )

    return success_response(
        {
            "totals": {
                "users": User.query.count(),
                "houses": total_houses,
                "bookings": Booking.query.count(),
                "contracts": Contract.query.count(),
                "payments": Payment.query.count(),
                "repairs": Repair.query.count(),
                "complaints": Complaint.query.count(),
                "news": News.query.count(),
                "paid_amount": float(paid_total or 0),
                "pending_payment_amount": float(pending_payment_total or 0),
                "occupancy_rate": round(rented_houses / total_houses, 4) if total_houses else 0,
                "active_users_30d": active_users_30d or 0,
            },
            "rent_income_trend": _rent_income_trend(),
            "houses_by_status": _count_by(House, House.status),
            "bookings_by_status": _count_by(Booking, Booking.status),
            "contracts_by_status": _count_by(Contract, Contract.status),
            "payments_by_status": _count_by(Payment, Payment.status),
            "repairs_by_status": _count_by(Repair, Repair.status),
            "complaints_by_status": _count_by(Complaint, Complaint.status),
            "news_by_status": _count_by(News, News.status),
        }
    )
