from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.schemas import AccountCreate, ProfileUpdate, SellerProfileCreate
from app.core.errors import DomainError
from app.database.models import AccountImage, GameAccount, SellerProfile, User, UserProfile, UserRole


class AccountService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def update_profile(self, user: User, changes: ProfileUpdate) -> UserProfile:
        profile = user.profile
        if profile is None:
            profile = UserProfile(display_name=changes.display_name or user.email.split("@", 1)[0])
            user.profile = profile
        for field, value in changes.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
        self.session.commit()
        self.session.refresh(profile)
        return profile

    def create_seller_profile(self, user: User, payload: SellerProfileCreate) -> SellerProfile:
        existing = self.session.scalar(select(SellerProfile.id).where(SellerProfile.user_id == user.id))
        if existing:
            raise DomainError("seller_profile_exists", "A seller profile already exists.", 409)
        if user.role == UserRole.BUYER:
            user.role = UserRole.SELLER
        seller = SellerProfile(user_id=user.id, shop_name=payload.shop_name.strip(), description=payload.description)
        self.session.add(seller)
        self.session.commit()
        self.session.refresh(seller)
        return seller

    def create_account(self, user: User, payload: AccountCreate) -> GameAccount:
        if user.role not in {UserRole.SELLER, UserRole.ADMIN} or user.seller_profile is None:
            raise DomainError("seller_profile_required", "Create a seller profile before adding game accounts.", 403)
        account = GameAccount(
            owner_id=user.id,
            title=payload.title.strip(),
            platform=payload.platform,
            team_strength=payload.team_strength,
            player_count=payload.player_count,
            coin_balance=payload.coin_balance,
            attributes=payload.attributes,
        )
        account.images = [AccountImage(image_url=url, position=i) for i, url in enumerate(payload.image_urls)]
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def get_owned_account(self, user: User, account_id: UUID) -> GameAccount:
        account = self.session.scalar(select(GameAccount).where(GameAccount.id == account_id, GameAccount.owner_id == user.id))
        if account is None:
            raise DomainError("account_not_found", "Game account was not found.", 404)
        return account
