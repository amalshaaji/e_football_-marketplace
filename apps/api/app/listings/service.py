from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.database.models import GameAccount, Listing, ListingStatus, User, UserRole
from app.listings.schemas import ListingCreate, ListingUpdate


class ListingService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, seller: User, payload: ListingCreate) -> Listing:
        account = self.session.scalar(select(GameAccount).where(GameAccount.id == payload.account_id, GameAccount.owner_id == seller.id))
        if account is None:
            raise DomainError("account_not_found", "An account you own is required to create a listing.", 404)
        listing = Listing(
            seller_id=seller.id,
            account_id=account.id,
            title=payload.title.strip(),
            description=payload.description,
            price_amount=payload.price_amount,
            currency=payload.currency.upper(),
            status=ListingStatus.PENDING_REVIEW,
            team_strength=account.team_strength,
        )
        self.session.add(listing)
        self.session.commit()
        self.session.refresh(listing)
        return listing

    def update(self, seller: User, listing_id: UUID, changes: ListingUpdate) -> Listing:
        listing = self.session.get(Listing, listing_id)
        if listing is None or (listing.seller_id != seller.id and seller.role != UserRole.ADMIN):
            raise DomainError("listing_not_found", "Listing was not found.", 404)
        if listing.status in {ListingStatus.SOLD, ListingStatus.RESERVED}:
            raise DomainError("listing_not_editable", "This listing can no longer be edited.", 409)
        for field, value in changes.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(listing, field, value.upper() if field == "currency" else value)
        self.session.commit()
        self.session.refresh(listing)
        return listing

    def archive(self, seller: User, listing_id: UUID) -> None:
        listing = self.session.get(Listing, listing_id)
        if listing is None or (listing.seller_id != seller.id and seller.role != UserRole.ADMIN):
            raise DomainError("listing_not_found", "Listing was not found.", 404)
        if listing.status in {ListingStatus.SOLD, ListingStatus.RESERVED}:
            raise DomainError("listing_not_archivable", "Reserved or sold listings cannot be archived.", 409)
        listing.status = ListingStatus.ARCHIVED
        self.session.commit()

    def search(self, *, query: str | None, min_price: float | None, max_price: float | None,
               min_strength: int | None, max_strength: int | None, sort: str,
               page: int, page_size: int) -> tuple[list[Listing], int]:
        statement = select(Listing).where(Listing.status == ListingStatus.ACTIVE)
        if query:
            statement = statement.where(Listing.title.ilike(f"%{query.strip()}%"))
        if min_price is not None:
            statement = statement.where(Listing.price_amount >= min_price)
        if max_price is not None:
            statement = statement.where(Listing.price_amount <= max_price)
        if min_strength is not None:
            statement = statement.where(Listing.team_strength >= min_strength)
        if max_strength is not None:
            statement = statement.where(Listing.team_strength <= max_strength)
        total = self.session.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
        order_by = {
            "price_asc": Listing.price_amount.asc(),
            "price_desc": Listing.price_amount.desc(),
            "strength_desc": Listing.team_strength.desc(),
        }.get(sort, Listing.created_at.desc())
        listings = list(self.session.scalars(statement.order_by(order_by, Listing.id).offset((page - 1) * page_size).limit(page_size)))
        return listings, total
