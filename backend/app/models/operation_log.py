from app.extensions import db
from app.models.base import ID_TYPE, utc_now


class OperationLog(db.Model):
    __tablename__ = "operation_logs"

    id = db.Column(ID_TYPE, primary_key=True)
    operator_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), index=True)
    module = db.Column(db.String(50), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)
    target_type = db.Column(db.String(50))
    target_id = db.Column(ID_TYPE)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    detail = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    operator = db.relationship("User", back_populates="operation_logs", lazy=True)
