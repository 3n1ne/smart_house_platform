from app.extensions import db
from app.models.base import ID_TYPE, utc_now


class Repair(db.Model):
    __tablename__ = "repairs"

    id = db.Column(ID_TYPE, primary_key=True)
    house_id = db.Column(ID_TYPE, db.ForeignKey("houses.id"), nullable=False, index=True)
    tenant_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), nullable=False, index=True)
    handler_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default="medium", nullable=False)
    status = db.Column(db.String(20), default="submitted", nullable=False, index=True)
    handled_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    house = db.relationship("House", back_populates="repairs", lazy=True)
    tenant = db.relationship(
        "User",
        foreign_keys=[tenant_id],
        back_populates="submitted_repairs",
        lazy=True,
    )
    handler = db.relationship(
        "User",
        foreign_keys=[handler_id],
        back_populates="handled_repairs",
        lazy=True,
    )
