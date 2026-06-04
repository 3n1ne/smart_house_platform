"""initial schema

Revision ID: 20260509_0001
Revises:
Create Date: 2026-05-09 00:00:00.000000
"""
from datetime import UTC, datetime

from alembic import op
import sqlalchemy as sa


revision = "20260509_0001"
down_revision = None
branch_labels = None
depends_on = None

ID_TYPE = sa.BigInteger().with_variant(sa.Integer(), "sqlite")


def _now():
    return datetime.now(UTC).replace(tzinfo=None)


def upgrade():
    op.create_table(
        "roles",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_roles_code", "roles", ["code"], unique=True)

    created_at = _now()
    op.bulk_insert(
        sa.table(
            "roles",
            sa.column("code", sa.String),
            sa.column("name", sa.String),
            sa.column("description", sa.String),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        [
            {
                "code": "admin",
                "name": "Administrator",
                "description": "System administrator",
                "created_at": created_at,
                "updated_at": created_at,
            },
            {
                "code": "landlord",
                "name": "Landlord",
                "description": "House owner",
                "created_at": created_at,
                "updated_at": created_at,
            },
            {
                "code": "tenant",
                "name": "Tenant",
                "description": "House renter",
                "created_at": created_at,
                "updated_at": created_at,
            },
        ],
    )

    op.create_table(
        "users",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("role_id", ID_TYPE, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("real_name", sa.String(length=80), nullable=True),
        sa.Column("avatar_url", sa.String(length=255), nullable=True),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("identity_no", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("is_mfa_enabled", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)
    op.create_index("ix_users_role_id", "users", ["role_id"], unique=False)
    op.create_index("ix_users_status", "users", ["status"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "houses",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("landlord_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("province", sa.String(length=50), nullable=True),
        sa.Column("city", sa.String(length=50), nullable=True),
        sa.Column("district", sa.String(length=50), nullable=True),
        sa.Column("community", sa.String(length=100), nullable=True),
        sa.Column("address_detail", sa.String(length=255), nullable=False),
        sa.Column("house_type", sa.String(length=50), nullable=True),
        sa.Column("layout", sa.String(length=50), nullable=True),
        sa.Column("area", sa.Numeric(10, 2), nullable=False),
        sa.Column("rent", sa.Numeric(10, 2), nullable=False),
        sa.Column("deposit", sa.Numeric(10, 2), nullable=False),
        sa.Column("decoration", sa.String(length=50), nullable=True),
        sa.Column("floor", sa.Integer(), nullable=True),
        sa.Column("total_floors", sa.Integer(), nullable=True),
        sa.Column("orientation", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_houses_city", "houses", ["city"], unique=False)
    op.create_index("ix_houses_district", "houses", ["district"], unique=False)
    op.create_index("ix_houses_landlord_id", "houses", ["landlord_id"], unique=False)
    op.create_index("ix_houses_layout", "houses", ["layout"], unique=False)
    op.create_index("ix_houses_status", "houses", ["status"], unique=False)

    op.create_table(
        "house_media",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("house_id", ID_TYPE, sa.ForeignKey("houses.id"), nullable=False),
        sa.Column("media_type", sa.String(length=20), nullable=False),
        sa.Column("file_url", sa.String(length=255), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_house_media_house_id", "house_media", ["house_id"], unique=False)

    op.create_table(
        "bookings",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("house_id", ID_TYPE, sa.ForeignKey("houses.id"), nullable=False),
        sa.Column("tenant_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("landlord_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("appointment_time", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("remark", sa.String(length=255), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_bookings_house_id", "bookings", ["house_id"], unique=False)
    op.create_index("ix_bookings_landlord_id", "bookings", ["landlord_id"], unique=False)
    op.create_index("ix_bookings_status", "bookings", ["status"], unique=False)
    op.create_index("ix_bookings_tenant_id", "bookings", ["tenant_id"], unique=False)

    op.create_table(
        "contracts",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("contract_no", sa.String(length=64), nullable=False),
        sa.Column("house_id", ID_TYPE, sa.ForeignKey("houses.id"), nullable=False),
        sa.Column("landlord_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tenant_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("monthly_rent", sa.Numeric(10, 2), nullable=False),
        sa.Column("deposit", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_cycle", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("signed_at", sa.DateTime(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_contracts_contract_no", "contracts", ["contract_no"], unique=True)
    op.create_index("ix_contracts_house_id", "contracts", ["house_id"], unique=False)
    op.create_index("ix_contracts_landlord_id", "contracts", ["landlord_id"], unique=False)
    op.create_index("ix_contracts_status", "contracts", ["status"], unique=False)
    op.create_index("ix_contracts_tenant_id", "contracts", ["tenant_id"], unique=False)

    op.create_table(
        "payments",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("contract_id", ID_TYPE, sa.ForeignKey("contracts.id"), nullable=False),
        sa.Column("payer_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("payee_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_type", sa.String(length=20), nullable=False),
        sa.Column("payment_method", sa.String(length=30), nullable=True),
        sa.Column("transaction_no", sa.String(length=100), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_payments_contract_id", "payments", ["contract_id"], unique=False)
    op.create_index("ix_payments_due_date", "payments", ["due_date"], unique=False)
    op.create_index("ix_payments_payee_id", "payments", ["payee_id"], unique=False)
    op.create_index("ix_payments_payer_id", "payments", ["payer_id"], unique=False)
    op.create_index("ix_payments_status", "payments", ["status"], unique=False)
    op.create_index("ix_payments_transaction_no", "payments", ["transaction_no"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("sender_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("receiver_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("house_id", ID_TYPE, sa.ForeignKey("houses.id"), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_messages_house_id", "messages", ["house_id"], unique=False)
    op.create_index("ix_messages_receiver_id", "messages", ["receiver_id"], unique=False)
    op.create_index("ix_messages_sender_id", "messages", ["sender_id"], unique=False)

    op.create_table(
        "news",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("author_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_news_author_id", "news", ["author_id"], unique=False)
    op.create_index("ix_news_status", "news", ["status"], unique=False)

    op.create_table(
        "repairs",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("house_id", ID_TYPE, sa.ForeignKey("houses.id"), nullable=False),
        sa.Column("tenant_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("handler_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("handled_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_repairs_handler_id", "repairs", ["handler_id"], unique=False)
    op.create_index("ix_repairs_house_id", "repairs", ["house_id"], unique=False)
    op.create_index("ix_repairs_status", "repairs", ["status"], unique=False)
    op.create_index("ix_repairs_tenant_id", "repairs", ["tenant_id"], unique=False)

    op.create_table(
        "complaints",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("house_id", ID_TYPE, sa.ForeignKey("houses.id"), nullable=True),
        sa.Column("complainant_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("handler_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("handled_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_complaints_complainant_id", "complaints", ["complainant_id"], unique=False)
    op.create_index("ix_complaints_handler_id", "complaints", ["handler_id"], unique=False)
    op.create_index("ix_complaints_house_id", "complaints", ["house_id"], unique=False)
    op.create_index("ix_complaints_status", "complaints", ["status"], unique=False)

    op.create_table(
        "operation_logs",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("operator_id", ID_TYPE, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("module", sa.String(length=50), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=True),
        sa.Column("target_id", ID_TYPE, nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_operation_logs_module", "operation_logs", ["module"], unique=False)
    op.create_index("ix_operation_logs_operator_id", "operation_logs", ["operator_id"], unique=False)


def downgrade():
    op.drop_table("operation_logs")
    op.drop_table("complaints")
    op.drop_table("repairs")
    op.drop_table("news")
    op.drop_table("messages")
    op.drop_table("payments")
    op.drop_table("contracts")
    op.drop_table("bookings")
    op.drop_table("house_media")
    op.drop_table("houses")
    op.drop_table("users")
    op.drop_table("roles")
