from app.extensions import db
from app.models.base import ID_TYPE, utc_now


class Contract(db.Model):
    __tablename__ = "contracts"

    id = db.Column(ID_TYPE, primary_key=True)
    contract_no = db.Column(db.String(64), unique=True, nullable=False, index=True)
    house_id = db.Column(ID_TYPE, db.ForeignKey("houses.id"), nullable=False, index=True)
    landlord_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False)
    deposit = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    payment_cycle = db.Column(db.String(20), default="monthly", nullable=False)
    status = db.Column(db.String(20), default="draft", nullable=False, index=True)
    signed_at = db.Column(db.DateTime)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    house = db.relationship("House", back_populates="contracts", lazy=True)
    landlord = db.relationship(
        "User",
        foreign_keys=[landlord_id],
        back_populates="landlord_contracts",
        lazy=True,
    )
    tenant = db.relationship(
        "User",
        foreign_keys=[tenant_id],
        back_populates="tenant_contracts",
        lazy=True,
    )
    payments = db.relationship("Payment", back_populates="contract", lazy=True)
