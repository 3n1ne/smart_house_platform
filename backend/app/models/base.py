from datetime import UTC, datetime

from app.extensions import db


ID_TYPE = db.BigInteger().with_variant(db.Integer, "sqlite")


def utc_now():
    return datetime.now(UTC).replace(tzinfo=None)


class TimestampMixin:
    created_at = None
    updated_at = None

    @classmethod
    def timestamp_columns(cls, db):
        return {
            "created_at": db.Column(db.DateTime, default=utc_now, nullable=False),
            "updated_at": db.Column(
                db.DateTime,
                default=utc_now,
                onupdate=utc_now,
                nullable=False,
            ),
        }
