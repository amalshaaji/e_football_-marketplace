from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CheckoutRequest(BaseModel):
    listing_id: UUID
    idempotency_key: str = Field(min_length=8, max_length=100)


class PaymentStartRequest(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=100)


class PaymentWebhook(BaseModel):
    event_id: str = Field(min_length=1, max_length=200)
    event_type: str = Field(min_length=1, max_length=100)
    provider_reference: str = Field(min_length=1, max_length=200)
    status: str = Field(pattern="^(succeeded|failed|refunded)$")


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    listing_id: UUID
    buyer_id: UUID
    seller_id: UUID
    total_amount: Decimal
    currency: str
    status: str
    created_at: datetime
    reservation_expires_at: datetime | None


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    provider: str
    provider_reference: str | None
    amount: Decimal
    currency: str
    status: str
