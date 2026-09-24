from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.dependencies import get_db
from app.core.errors import DomainError
from app.database.models import Favorite, Listing, ListingStatus, User

router = APIRouter()


@router.get("")
def list_favorites(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> list[dict]:
    rows = db.execute(select(Favorite, Listing).join(Listing, Favorite.listing_id == Listing.id).where(Favorite.user_id == user.id).order_by(Favorite.created_at.desc())).all()
    return [{"id": str(favorite.id), "listing_id": str(listing.id), "title": listing.title, "price_amount": str(listing.price_amount), "currency": listing.currency, "team_strength": listing.team_strength, "status": listing.status.value} for favorite, listing in rows]


@router.put("/{listing_id}", status_code=204)
def add_favorite(listing_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> Response:
    listing = db.scalar(select(Listing).where(Listing.id == listing_id, Listing.status == ListingStatus.ACTIVE))
    if listing is None:
        raise DomainError("listing_not_found", "Active listing was not found.", 404)
    favorite = db.scalar(select(Favorite).where(Favorite.user_id == user.id, Favorite.listing_id == listing_id))
    if favorite is None:
        db.add(Favorite(user_id=user.id, listing_id=listing_id))
        db.commit()
    return Response(status_code=204)


@router.delete("/{listing_id}", status_code=204)
def remove_favorite(listing_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> Response:
    favorite = db.scalar(select(Favorite).where(Favorite.user_id == user.id, Favorite.listing_id == listing_id))
    if favorite:
        db.delete(favorite)
        db.commit()
    return Response(status_code=204)
