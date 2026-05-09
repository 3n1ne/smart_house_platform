from app.extensions import db
from app.models.base import ID_TYPE, utc_now


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(ID_TYPE, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    users = db.relationship("User", back_populates="role", lazy=True)
