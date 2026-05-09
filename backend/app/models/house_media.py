from app.extensions import db
from app.models.base import ID_TYPE, utc_now


class HouseMedia(db.Model):
    __tablename__ = "house_media"

    id = db.Column(ID_TYPE, primary_key=True)
    house_id = db.Column(ID_TYPE, db.ForeignKey("houses.id"), nullable=False, index=True)
    media_type = db.Column(db.String(20), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    house = db.relationship("House", back_populates="media_items", lazy=True)
