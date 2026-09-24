from app.database.base import Base
from app.database import models as _models  # noqa: F401


def test_core_marketplace_tables_are_registered_for_migrations() -> None:
    expected = {
        "users",
        "user_profiles",
        "seller_profiles",
        "accounts",
        "account_images",
        "listings",
        "orders",
        "payments",
        "reviews",
        "favorites",
        "conversations",
        "messages",
        "notifications",
        "reports",
        "audit_logs",
    }

    assert expected <= set(Base.metadata.tables)


def test_marketplace_integrity_constraints_are_registered() -> None:
    assert "uq_favorite_user_listing" in {
        constraint.name
        for constraint in Base.metadata.tables["favorites"].constraints
    }
    assert "uq_review_order" in {
        constraint.name
        for constraint in Base.metadata.tables["reviews"].constraints
    }
    assert "ix_listings_price" in {
        index.name for index in Base.metadata.tables["listings"].indexes
    }
