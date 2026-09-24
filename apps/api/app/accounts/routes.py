from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.accounts.schemas import AccountCreate, AccountResponse, ProfileUpdate, SellerProfileCreate, SellerProfileResponse
from app.accounts.service import AccountService
from app.auth.dependencies import get_current_user
from app.core.dependencies import get_db
from app.database.models import User

router = APIRouter()


@router.patch("/profile")
def update_profile(payload: ProfileUpdate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    profile = AccountService(db).update_profile(user, payload)
    return {"display_name": profile.display_name, "bio": profile.bio, "country_code": profile.country_code}


@router.post("/seller-profile", response_model=SellerProfileResponse, status_code=status.HTTP_201_CREATED)
def create_seller_profile(payload: SellerProfileCreate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> SellerProfileResponse:
    return AccountService(db).create_seller_profile(user, payload)


@router.get("/seller-profile", response_model=SellerProfileResponse)
def get_seller_profile(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> SellerProfileResponse:
    from sqlalchemy import select
    from app.core.errors import DomainError
    from app.database.models import SellerProfile

    profile = db.scalar(select(SellerProfile).where(SellerProfile.user_id == user.id))
    if profile is None:
        raise DomainError("seller_profile_not_found", "Set up a seller profile to manage listings.", 404)
    return profile


@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> AccountResponse:
    return AccountService(db).create_account(user, payload)


@router.get("/accounts", response_model=list[AccountResponse])
def list_my_accounts(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> list[AccountResponse]:
    from sqlalchemy import select
    from app.database.models import GameAccount

    return list(db.scalars(select(GameAccount).where(GameAccount.owner_id == user.id).order_by(GameAccount.created_at.desc())))
