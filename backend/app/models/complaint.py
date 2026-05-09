from app.extensions import db
from app.models.base import ID_TYPE, utc_now


class Complaint(db.Model):
    __tablename__ = "complaints"

    id = db.Column(ID_TYPE, primary_key=True)
    house_id = db.Column(ID_TYPE, db.ForeignKey("houses.id"), index=True)
    complainant_id = db.Column(
        ID_TYPE,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    handler_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), index=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="submitted", nullable=False, index=True)
    result = db.Column(db.Text)
    handled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    house = db.relationship("House", back_populates="complaints", lazy=True)
    complainant = db.relationship(
        "User",
        foreign_keys=[complainant_id],
        back_populates="complaints",
        lazy=True,
    )
    handler = db.relationship(
        "User",
        foreign_keys=[handler_id],
        back_populates="handled_complaints",
        lazy=True,
    )
