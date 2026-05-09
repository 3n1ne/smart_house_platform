from app.extensions import db
from app.models.base import ID_TYPE, utc_now


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(ID_TYPE, primary_key=True)
    role_id = db.Column(ID_TYPE, db.ForeignKey("roles.id"), nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20), unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(80))
    avatar_url = db.Column(db.String(255))
    gender = db.Column(db.String(20))
    identity_no = db.Column(db.String(64))
    status = db.Column(db.String(20), default="active", nullable=False, index=True)
    is_mfa_enabled = db.Column(db.Boolean, default=False, nullable=False)
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    role = db.relationship("Role", back_populates="users", lazy=True)
    houses = db.relationship(
        "House",
        foreign_keys="House.landlord_id",
        back_populates="landlord",
        lazy=True,
    )
    tenant_bookings = db.relationship(
        "Booking",
        foreign_keys="Booking.tenant_id",
        back_populates="tenant",
        lazy=True,
    )
    landlord_bookings = db.relationship(
        "Booking",
        foreign_keys="Booking.landlord_id",
        back_populates="landlord",
        lazy=True,
    )
    landlord_contracts = db.relationship(
        "Contract",
        foreign_keys="Contract.landlord_id",
        back_populates="landlord",
        lazy=True,
    )
    tenant_contracts = db.relationship(
        "Contract",
        foreign_keys="Contract.tenant_id",
        back_populates="tenant",
        lazy=True,
    )
    sent_messages = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender",
        lazy=True,
    )
    received_messages = db.relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        back_populates="receiver",
        lazy=True,
    )
    news_items = db.relationship("News", back_populates="author", lazy=True)
    submitted_repairs = db.relationship(
        "Repair",
        foreign_keys="Repair.tenant_id",
        back_populates="tenant",
        lazy=True,
    )
    handled_repairs = db.relationship(
        "Repair",
        foreign_keys="Repair.handler_id",
        back_populates="handler",
        lazy=True,
    )
    complaints = db.relationship(
        "Complaint",
        foreign_keys="Complaint.complainant_id",
        back_populates="complainant",
        lazy=True,
    )
    handled_complaints = db.relationship(
        "Complaint",
        foreign_keys="Complaint.handler_id",
        back_populates="handler",
        lazy=True,
    )
    initiated_payments = db.relationship(
        "Payment",
        foreign_keys="Payment.payer_id",
        back_populates="payer",
        lazy=True,
    )
    received_payments = db.relationship(
        "Payment",
        foreign_keys="Payment.payee_id",
        back_populates="payee",
        lazy=True,
    )
    operation_logs = db.relationship("OperationLog", back_populates="operator", lazy=True)
