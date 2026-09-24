from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    order_id: UUID
    rating: int = Field(ge=1, le=5)
    body: str | None = Field(default=None, max_length=2000)


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    order_id: UUID
    author_id: UUID
    seller_id: UUID
    rating: int
    body: str | None
    created_at: datetime


class ConversationCreate(BaseModel):
    listing_id: UUID
    body: str = Field(min_length=1, max_length=5000)


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    body: str
    created_at: datetime
    read_at: datetime | None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    buyer_id: UUID
    seller_id: UUID
    listing_id: UUID | None
    created_at: datetime
    messages: list[MessageResponse] = []
