from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.dependencies import get_db
from app.database.models import Listing, User
from app.core.errors import DomainError
from app.database.models import ListingStatus
from app.listings.schemas import ListingCreate, ListingPage, ListingResponse, ListingUpdate
from app.listings.service import ListingService

router = APIRouter()


@router.get("", response_model=ListingPage)
def search_listings(
    db: Annotated[Session, Depends(get_db)],
    q: str | None = Query(default=None, max_length=120),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    min_strength: int | None = Query(default=None, ge=0),
    max_strength: int | None = Query(default=None, ge=0),
    sort: str = Query(default="newest", pattern="^(newest|price_asc|price_desc|strength_desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=24, ge=1, le=100),
) -> dict:
    items, total = ListingService(db).search(query=q, min_price=min_price, max_price=max_price, min_strength=min_strength, max_strength=max_strength, sort=sort, page=page, page_size=page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/seller/mine", response_model=list[ListingResponse])
def my_listings(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> list[Listing]:
    return list(db.scalars(select(Listing).where(Listing.seller_id == user.id).order_by(Listing.created_at.desc())))


@router.get("/{listing_id}", response_model=ListingResponse)
def listing_detail(listing_id: UUID, db: Annotated[Session, Depends(get_db)]) -> Listing:
    listing = db.scalar(select(Listing).where(Listing.id == listing_id, Listing.status == ListingStatus.ACTIVE))
    if listing is None:
        raise DomainError("listing_not_found", "Listing was not found.", 404)
    return listing


@router.post("", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(payload: ListingCreate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> Listing:
    return ListingService(db).create(user, payload)


@router.patch("/{listing_id}", response_model=ListingResponse)
def update_listing(listing_id: UUID, payload: ListingUpdate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> Listing:
    return ListingService(db).update(user, listing_id, payload)


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_listing(listing_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> Response:
    ListingService(db).archive(user, listing_id)
    return Response(status_code=204)
