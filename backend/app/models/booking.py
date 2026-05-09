from app.extensions import db
from app.models.base import ID_TYPE, utc_now


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(ID_TYPE, primary_key=True)
    house_id = db.Column(ID_TYPE, db.ForeignKey("houses.id"), nullable=False, index=True)
    tenant_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), nullable=False, index=True)
    landlord_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), nullable=False, index=True)
    appointment_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False, index=True)
    remark = db.Column(db.String(255))
    confirmed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    house = db.relationship("House", back_populates="bookings", lazy=True)
    tenant = db.relationship(
        "User",
        foreign_keys=[tenant_id],
        back_populates="tenant_bookings",
        lazy=True,
    )
    landlord = db.relationship(
        "User",
        foreign_keys=[landlord_id],
        back_populates="landlord_bookings",
        lazy=True,
    )
