from app.extensions import db
from app.models.base import ID_TYPE, utc_now


class House(db.Model):
    __tablename__ = "houses"

    id = db.Column(ID_TYPE, primary_key=True)
    landlord_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    province = db.Column(db.String(50))
    city = db.Column(db.String(50), index=True)
    district = db.Column(db.String(50), index=True)
    community = db.Column(db.String(100))
    address_detail = db.Column(db.String(255), nullable=False)
    house_type = db.Column(db.String(50))
    layout = db.Column(db.String(50), index=True)
    area = db.Column(db.Numeric(10, 2), nullable=False)
    rent = db.Column(db.Numeric(10, 2), nullable=False)
    deposit = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    decoration = db.Column(db.String(50))
    floor = db.Column(db.Integer)
    total_floors = db.Column(db.Integer)
    orientation = db.Column(db.String(50))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="draft", nullable=False, index=True)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    landlord = db.relationship("User", back_populates="houses", lazy=True)
    media_items = db.relationship("HouseMedia", back_populates="house", lazy=True)
    bookings = db.relationship("Booking", back_populates="house", lazy=True)
    contracts = db.relationship("Contract", back_populates="house", lazy=True)
    messages = db.relationship("Message", back_populates="house", lazy=True)
    repairs = db.relationship("Repair", back_populates="house", lazy=True)
    complaints = db.relationship("Complaint", back_populates="house", lazy=True)
