"""expand identity field for encrypted values

Revision ID: 20260521_0002
Revises: 20260509_0001
Create Date: 2026-05-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "20260521_0002"
down_revision = "20260509_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "users",
        "identity_no",
        existing_type=sa.String(length=64),
        type_=sa.String(length=255),
        existing_nullable=True,
    )


def downgrade():
    op.alter_column(
        "users",
        "identity_no",
        existing_type=sa.String(length=255),
        type_=sa.String(length=64),
        existing_nullable=True,
    )
