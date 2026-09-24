from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=80)
    bio: str | None = Field(default=None, max_length=2000)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)


class SellerProfileCreate(BaseModel):
    shop_name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=2000)


class SellerProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    shop_name: str
    description: str | None
    rating_average: Decimal
    completed_sales: int


class AccountCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    platform: str = Field(min_length=2, max_length=32)
    team_strength: int = Field(ge=0, le=10000)
    player_count: int = Field(ge=0, le=100)
    coin_balance: int = Field(default=0, ge=0)
    attributes: dict = Field(default_factory=dict)
    image_urls: list[str] = Field(default_factory=list, max_length=12)


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    platform: str
    team_strength: int
    player_count: int
    coin_balance: int
    attributes: dict
