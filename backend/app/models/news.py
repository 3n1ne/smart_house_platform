from app.extensions import db
from app.models.base import ID_TYPE, utc_now


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(ID_TYPE, primary_key=True)
    author_id = db.Column(ID_TYPE, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="draft", nullable=False, index=True)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    author = db.relationship("User", back_populates="news_items", lazy=True)
