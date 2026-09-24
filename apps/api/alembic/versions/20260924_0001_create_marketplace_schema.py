"""create marketplace schema

Revision ID: 20260924_0001
Revises:
Create Date: 2026-09-24 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260924_0001"
down_revision = None
branch_labels = None
depends_on = None


user_role = sa.Enum("BUYER", "SELLER", "ADMIN", name="user_role", create_type=False)
listing_status = sa.Enum(
    "DRAFT", "PENDING_REVIEW", "ACTIVE", "RESERVED", "SOLD", "ARCHIVED", "REJECTED",
    name="listing_status", create_type=False,
)
order_status = sa.Enum(
    "PAYMENT_PENDING", "PAID", "DELIVERY_PENDING", "COMPLETED", "CANCELLED", "REFUNDED", "DISPUTED",
    name="order_status", create_type=False,
)
payment_status = sa.Enum("PENDING", "REQUIRES_ACTION", "SUCCEEDED", "FAILED", "REFUNDED", name="payment_status", create_type=False)
report_status = sa.Enum("OPEN", "UNDER_REVIEW", "RESOLVED", "DISMISSED", name="report_status", create_type=False)


def _timestamps():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    bind = op.get_bind()
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="BUYER"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_timestamps(),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role_created", "users", ["role", "created_at"])

    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("display_name", sa.String(80), nullable=False),
        sa.Column("avatar_url", sa.String(2048)),
        sa.Column("bio", sa.Text()),
        sa.Column("country_code", sa.String(2)),
        *_timestamps(),
    )
    op.create_table(
        "seller_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("shop_name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("rating_average", sa.Numeric(3, 2), nullable=False, server_default="0"),
        sa.Column("completed_sales", sa.Integer(), nullable=False, server_default="0"),
        *_timestamps(),
        sa.CheckConstraint("rating_average >= 0 AND rating_average <= 5", name="ck_seller_rating_range"),
    )
    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("platform", sa.String(32), nullable=False),
        sa.Column("team_strength", sa.Integer(), nullable=False),
        sa.Column("player_count", sa.Integer(), nullable=False),
        sa.Column("coin_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attributes", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        *_timestamps(),
        sa.CheckConstraint("team_strength >= 0", name="ck_account_team_strength_nonnegative"),
    )
    op.create_index("ix_accounts_owner_id", "accounts", ["owner_id"])
    op.create_table(
        "listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("seller_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id", ondelete="RESTRICT"), unique=True, nullable=False),
        sa.Column("title", sa.String(140), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("price_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("status", listing_status, nullable=False, server_default="DRAFT"),
        sa.Column("team_strength", sa.Integer(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        *_timestamps(),
        sa.CheckConstraint("price_amount > 0", name="ck_listing_price_positive"),
    )
    op.create_index("ix_listings_seller_id", "listings", ["seller_id"])
    op.create_index("ix_listings_marketplace", "listings", ["status", "created_at"])
    op.create_index("ix_listings_strength", "listings", ["status", "team_strength"])
    op.create_index("ix_listings_price", "listings", ["status", "price_amount"])
    op.create_table(
        "account_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("image_url", sa.String(2048), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        *_timestamps(),
        sa.UniqueConstraint("account_id", "position", name="uq_account_image_position"),
    )
    op.create_index("ix_account_images_account_id", "account_images", ["account_id"])
    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("seller_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("status", order_status, nullable=False, server_default="PAYMENT_PENDING"),
        sa.Column("idempotency_key", sa.String(100), nullable=False, unique=True),
        sa.Column("reservation_expires_at", sa.DateTime(timezone=True)),
        *_timestamps(),
        sa.CheckConstraint("total_amount > 0", name="ck_order_total_positive"),
    )
    op.create_index("ix_orders_buyer_created", "orders", ["buyer_id", "created_at"])
    op.create_index("ix_orders_seller_created", "orders", ["seller_id", "created_at"])
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="RESTRICT"), unique=True, nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("provider_reference", sa.String(200)),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("status", payment_status, nullable=False, server_default="PENDING"),
        sa.Column("idempotency_key", sa.String(100), unique=True, nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("provider", "provider_reference", name="uq_payment_provider_reference"),
    )
    op.create_index("ix_payments_status_created", "payments", ["status", "created_at"])
    op.create_table(
        "payment_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("provider_event_id", sa.String(200), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("provider", "provider_event_id", name="uq_payment_event_provider_id"),
    )
    op.create_index("ix_payment_events_payment_id", "payment_events", ["payment_id"])
    op.create_table(
        "favorites",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("user_id", "listing_id", name="uq_favorite_user_listing"),
    )
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"])
    op.create_index("ix_favorites_listing_id", "favorites", ["listing_id"])
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("seller_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="SET NULL")),
        *_timestamps(),
        sa.UniqueConstraint("buyer_id", "seller_id", "listing_id", name="uq_conversation_participants_listing"),
    )
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True)),
        *_timestamps(),
    )
    op.create_index("ix_messages_conversation_created", "messages", ["conversation_id", "created_at"])
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("read_at", sa.DateTime(timezone=True)),
        *_timestamps(),
    )
    op.create_index("ix_notifications_user_unread", "notifications", ["user_id", "read_at", "created_at"])
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("reporter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="SET NULL")),
        sa.Column("reported_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("reason", sa.String(100), nullable=False),
        sa.Column("details", sa.Text()),
        sa.Column("status", report_status, nullable=False, server_default="OPEN"),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        *_timestamps(),
    )
    op.create_index("ix_reports_status_created", "reports", ["status", "created_at"])
    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("seller_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text()),
        sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_timestamps(),
        sa.UniqueConstraint("order_id", name="uq_review_order"),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_review_rating_range"),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(80), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True)),
        sa.Column("details", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_logs_actor_created", "audit_logs", ["actor_id", "created_at"])
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])


def downgrade() -> None:
    for table in (
        "audit_logs", "reviews", "reports", "notifications", "messages", "conversations",
        "favorites", "payment_events", "payments", "orders", "account_images", "listings", "accounts",
        "seller_profiles", "user_profiles", "users",
    ):
        op.drop_table(table)
    bind = op.get_bind()
    for enum_type in (report_status, payment_status, order_status, listing_status, user_role):
        enum_type.drop(bind, checkfirst=True)
