from app.extensions import db
from app.models.base import ID_TYPE, utc_now


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(ID_TYPE, primary_key=True)
    sender_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), nullable=False, index=True)
    house_id = db.Column(ID_TYPE, db.ForeignKey("houses.id"), index=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    sender = db.relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages",
        lazy=True,
    )
    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_messages",
        lazy=True,
    )
    house = db.relationship("House", back_populates="messages", lazy=True)
