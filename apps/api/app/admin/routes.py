from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.core.dependencies import get_db
from app.core.errors import DomainError
from app.database.models import AuditLog, Listing, ListingStatus, Order, Payment, Report, ReportStatus, Review, User, UserRole
from app.admin.schemas import ListingModeration, ReportModeration, UserStatusUpdate

router = APIRouter()
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]


def _audit(db: Session, actor: User, action: str, entity_type: str, entity_id: UUID, details: dict) -> None:
    db.add(AuditLog(actor_id=actor.id, action=action, entity_type=entity_type, entity_id=entity_id, details=details))


@router.get("/stats")
def platform_stats(_admin: AdminUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    def count(model, *criteria) -> int:
        return db.scalar(select(func.count()).select_from(model).where(*criteria)) or 0

    return {
        "users": count(User),
        "active_users": count(User, User.is_active.is_(True)),
        "active_listings": count(Listing, Listing.status == ListingStatus.ACTIVE),
        "pending_listings": count(Listing, Listing.status == ListingStatus.PENDING_REVIEW),
        "open_reports": count(Report, Report.status.in_([ReportStatus.OPEN, ReportStatus.UNDER_REVIEW])),
        "orders": count(Order),
        "payments": count(Payment),
    }


@router.get("/users")
def list_users(_admin: AdminUser, db: Annotated[Session, Depends(get_db)], page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100)) -> dict:
    total = db.scalar(select(func.count()).select_from(User)) or 0
    users = db.scalars(select(User).order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size))
    return {"items": [{"id": str(user.id), "email": user.email, "role": user.role.value, "is_active": user.is_active, "created_at": user.created_at} for user in users], "total": total, "page": page, "page_size": page_size}


@router.patch("/users/{user_id}/status")
def update_user_status(user_id: UUID, payload: UserStatusUpdate, admin: AdminUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    user = db.get(User, user_id)
    if user is None:
        raise DomainError("user_not_found", "User was not found.", 404)
    if user.id == admin.id and not payload.is_active:
        raise DomainError("cannot_disable_self", "You cannot disable your own administrator account.", 409)
    previous = user.is_active
    user.is_active = payload.is_active
    _audit(db, admin, "user.status_changed", "user", user.id, {"from": previous, "to": user.is_active})
    db.commit()
    return {"id": str(user.id), "is_active": user.is_active}


@router.get("/listings")
def moderation_listings(_admin: AdminUser, db: Annotated[Session, Depends(get_db)], status_filter: ListingStatus = Query(ListingStatus.PENDING_REVIEW), page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100)) -> dict:
    statement = select(Listing).where(Listing.status == status_filter)
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    items = db.scalars(statement.order_by(Listing.created_at.asc()).offset((page - 1) * page_size).limit(page_size))
    return {"items": [_listing(item) for item in items], "total": total, "page": page, "page_size": page_size}


@router.patch("/listings/{listing_id}/moderation")
def moderate_listing(listing_id: UUID, payload: ListingModeration, admin: AdminUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise DomainError("listing_not_found", "Listing was not found.", 404)
    if listing.status != ListingStatus.PENDING_REVIEW:
        raise DomainError("listing_not_pending", "Only listings awaiting review can be moderated.", 409)
    listing.status = ListingStatus(payload.status)
    if listing.status == ListingStatus.ACTIVE:
        from datetime import UTC, datetime
        listing.published_at = datetime.now(UTC)
    _audit(db, admin, "listing.moderated", "listing", listing.id, {"status": listing.status.value})
    db.commit()
    return _listing(listing)


@router.get("/reports")
def list_reports(_admin: AdminUser, db: Annotated[Session, Depends(get_db)], status_filter: ReportStatus | None = Query(None), page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100)) -> dict:
    statement = select(Report)
    if status_filter:
        statement = statement.where(Report.status == status_filter)
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    items = db.scalars(statement.order_by(Report.created_at.asc()).offset((page - 1) * page_size).limit(page_size))
    return {"items": [_report(item) for item in items], "total": total, "page": page, "page_size": page_size}


@router.patch("/reports/{report_id}")
def moderate_report(report_id: UUID, payload: ReportModeration, admin: AdminUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    report = db.get(Report, report_id)
    if report is None:
        raise DomainError("report_not_found", "Report was not found.", 404)
    report.status = ReportStatus(payload.status)
    report.reviewed_by = admin.id
    _audit(db, admin, "report.moderated", "report", report.id, {"status": report.status.value})
    db.commit()
    return _report(report)


@router.get("/orders")
def inspect_orders(_admin: AdminUser, db: Annotated[Session, Depends(get_db)], page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100)) -> dict:
    total = db.scalar(select(func.count()).select_from(Order)) or 0
    items = db.scalars(select(Order).order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size))
    return {"items": [_order(item) for item in items], "total": total, "page": page, "page_size": page_size}


@router.get("/payments")
def inspect_payments(_admin: AdminUser, db: Annotated[Session, Depends(get_db)], page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100)) -> dict:
    total = db.scalar(select(func.count()).select_from(Payment)) or 0
    items = db.scalars(select(Payment).order_by(Payment.created_at.desc()).offset((page - 1) * page_size).limit(page_size))
    return {"items": [{"id": str(item.id), "order_id": str(item.order_id), "provider": item.provider, "provider_reference": item.provider_reference, "amount": str(item.amount), "currency": item.currency, "status": item.status.value, "created_at": item.created_at} for item in items], "total": total, "page": page, "page_size": page_size}


@router.get("/reviews")
def inspect_reviews(_admin: AdminUser, db: Annotated[Session, Depends(get_db)], include_hidden: bool = False, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100)) -> dict:
    statement = select(Review)
    if not include_hidden:
        statement = statement.where(Review.is_hidden.is_(False))
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    items = db.scalars(statement.order_by(Review.created_at.desc()).offset((page - 1) * page_size).limit(page_size))
    return {"items": [{"id": str(item.id), "order_id": str(item.order_id), "author_id": str(item.author_id), "seller_id": str(item.seller_id), "rating": item.rating, "body": item.body, "is_hidden": item.is_hidden, "created_at": item.created_at} for item in items], "total": total, "page": page, "page_size": page_size}


@router.get("/audit-logs")
def audit_history(_admin: AdminUser, db: Annotated[Session, Depends(get_db)], page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100)) -> dict:
    total = db.scalar(select(func.count()).select_from(AuditLog)) or 0
    items = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size))
    return {"items": [{"id": str(item.id), "actor_id": str(item.actor_id) if item.actor_id else None, "action": item.action, "entity_type": item.entity_type, "entity_id": str(item.entity_id) if item.entity_id else None, "details": item.details, "created_at": item.created_at} for item in items], "total": total, "page": page, "page_size": page_size}


def _listing(item: Listing) -> dict:
    return {"id": str(item.id), "seller_id": str(item.seller_id), "account_id": str(item.account_id), "title": item.title, "description": item.description, "price_amount": str(item.price_amount), "currency": item.currency, "team_strength": item.team_strength, "status": item.status.value, "created_at": item.created_at}


def _report(item: Report) -> dict:
    return {"id": str(item.id), "reporter_id": str(item.reporter_id), "listing_id": str(item.listing_id) if item.listing_id else None, "reported_user_id": str(item.reported_user_id) if item.reported_user_id else None, "reason": item.reason, "details": item.details, "status": item.status.value, "created_at": item.created_at, "reviewed_by": str(item.reviewed_by) if item.reviewed_by else None}


def _order(item: Order) -> dict:
    return {"id": str(item.id), "listing_id": str(item.listing_id), "buyer_id": str(item.buyer_id), "seller_id": str(item.seller_id), "total_amount": str(item.total_amount), "currency": item.currency, "status": item.status.value, "created_at": item.created_at}
