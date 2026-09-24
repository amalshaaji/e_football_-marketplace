from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.dependencies import get_db
from app.database.models import Order, Payment, User
from app.orders.schemas import CheckoutRequest, OrderResponse, PaymentResponse, PaymentStartRequest, PaymentWebhook
from app.orders.service import OrderService

router = APIRouter()


@router.post("/checkout", response_model=OrderResponse, status_code=201)
def checkout(payload: CheckoutRequest, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> Order:
    return OrderService(db).checkout(user, payload)


@router.get("/mine", response_model=list[OrderResponse])
def my_orders(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> list[Order]:
    return list(db.scalars(select(Order).where(Order.buyer_id == user.id).order_by(Order.created_at.desc())))


@router.get("/seller/mine", response_model=list[OrderResponse])
def seller_orders(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> list[Order]:
    return list(db.scalars(select(Order).where(Order.seller_id == user.id).order_by(Order.created_at.desc())))


@router.get("/{order_id}", response_model=OrderResponse)
def order_detail(order_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> Order:
    order = db.get(Order, order_id)
    if order is None or user.id not in {order.buyer_id, order.seller_id}:
        from app.core.errors import DomainError
        raise DomainError("order_not_found", "Order was not found.", 404)
    return order


@router.post("/{order_id}/payment", response_model=PaymentResponse)
def start_payment(order_id: UUID, payload: PaymentStartRequest, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> Payment:
    return OrderService(db).start_payment(user, order_id, payload.idempotency_key)


@router.post("/webhooks/{provider}", response_model=PaymentResponse)
def payment_webhook(provider: str, payload: PaymentWebhook, db: Annotated[Session, Depends(get_db)], x_payment_signature: Annotated[str, Header()]) -> Payment:
    from app.core.errors import DomainError

    return OrderService(db).process_webhook(payload, x_payment_signature, provider)
