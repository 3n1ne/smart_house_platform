from app.extensions import db
from app.models.base import ID_TYPE, utc_now


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(ID_TYPE, primary_key=True)
    contract_id = db.Column(ID_TYPE, db.ForeignKey("contracts.id"), nullable=False, index=True)
    payer_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), nullable=False, index=True)
    payee_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(30))
    transaction_no = db.Column(db.String(100), index=True)
    due_date = db.Column(db.Date, index=True)
    paid_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="pending", nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    contract = db.relationship("Contract", back_populates="payments", lazy=True)
    payer = db.relationship(
        "User",
        foreign_keys=[payer_id],
        back_populates="initiated_payments",
        lazy=True,
    )
    payee = db.relationship(
        "User",
        foreign_keys=[payee_id],
        back_populates="received_payments",
        lazy=True,
    )
