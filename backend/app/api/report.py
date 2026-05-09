from flask import Blueprint
from sqlalchemy import func

from app.extensions import db
from app.models.booking import Booking
from app.models.complaint import Complaint
from app.models.contract import Contract
from app.models.house import House
from app.models.news import News
from app.models.payment import Payment
from app.models.repair import Repair
from app.models.user import User
from app.utils.api_response import success_response
from app.utils.auth import roles_required


report_bp = Blueprint("report", __name__)


def _count_by(model, column):
    rows = db.session.query(column, func.count(model.id)).group_by(column).all()
    return {key or "unknown": count for key, count in rows}


@report_bp.get("/overview")
@roles_required("admin")
def overview():
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

    return success_response(
        {
            "totals": {
                "users": User.query.count(),
                "houses": House.query.count(),
                "bookings": Booking.query.count(),
                "contracts": Contract.query.count(),
                "payments": Payment.query.count(),
                "repairs": Repair.query.count(),
                "complaints": Complaint.query.count(),
                "news": News.query.count(),
                "paid_amount": float(paid_total or 0),
                "pending_payment_amount": float(pending_payment_total or 0),
            },
            "houses_by_status": _count_by(House, House.status),
            "bookings_by_status": _count_by(Booking, Booking.status),
            "contracts_by_status": _count_by(Contract, Contract.status),
            "payments_by_status": _count_by(Payment, Payment.status),
            "repairs_by_status": _count_by(Repair, Repair.status),
            "complaints_by_status": _count_by(Complaint, Complaint.status),
            "news_by_status": _count_by(News, News.status),
        }
    )
