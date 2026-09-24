from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ListingCreate(BaseModel):
    account_id: UUID
    title: str = Field(min_length=3, max_length=140)
    description: str = Field(default="", max_length=5000)
    price_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class ListingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=140)
    description: str | None = Field(default=None, max_length=5000)
    price_amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    currency: str | None = Field(default=None, min_length=3, max_length=3)


class ListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str
    price_amount: Decimal
    currency: str
    status: str
    team_strength: int
    account_id: UUID


class ListingPage(BaseModel):
    items: list[ListingResponse]
    total: int
    page: int
    page_size: int
