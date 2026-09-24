from datetime import UTC, datetime, timedelta
import hashlib
import hmac
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import DomainError
from app.database.models import Listing, ListingStatus, Order, OrderStatus, Payment, PaymentEvent, PaymentStatus, User
from app.orders.providers import PaymentProvider, UnconfiguredProvider
from app.orders.schemas import CheckoutRequest, PaymentWebhook


class OrderService:
    def __init__(self, session: Session, provider: PaymentProvider | None = None) -> None:
        self.session = session
        self.provider = provider or UnconfiguredProvider()

    def checkout(self, buyer: User, payload: CheckoutRequest) -> Order:
        previous = self.session.scalar(select(Order).where(Order.idempotency_key == payload.idempotency_key))
        if previous:
            if previous.buyer_id != buyer.id:
                raise DomainError("idempotency_conflict", "This checkout key belongs to another account.", 409)
            return previous
        listing = self.session.scalar(select(Listing).where(Listing.id == payload.listing_id).with_for_update())
        if listing is None or listing.status != ListingStatus.ACTIVE:
            raise DomainError("listing_unavailable", "This listing is no longer available.", 409)
        if listing.seller_id == buyer.id:
            raise DomainError("cannot_buy_own_listing", "You cannot purchase your own listing.", 409)
        now = datetime.now(UTC)
        order = Order(
            listing_id=listing.id,
            buyer_id=buyer.id,
            seller_id=listing.seller_id,
            total_amount=listing.price_amount,
            currency=listing.currency,
            status=OrderStatus.PAYMENT_PENDING,
            idempotency_key=payload.idempotency_key,
            reservation_expires_at=now + timedelta(minutes=20),
        )
        listing.status = ListingStatus.RESERVED
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    def start_payment(self, buyer: User, order_id: UUID, idempotency_key: str) -> Payment:
        order = self.session.scalar(select(Order).where(Order.id == order_id).with_for_update())
        if order is None or order.buyer_id != buyer.id:
            raise DomainError("order_not_found", "Order was not found.", 404)
        existing = self.session.scalar(select(Payment).where(Payment.order_id == order.id))
        if existing:
            return existing
        if order.status != OrderStatus.PAYMENT_PENDING:
            raise DomainError("order_not_payable", "This order cannot accept a payment.", 409)
        if order.reservation_expires_at and order.reservation_expires_at <= datetime.now(UTC):
            self._release_expired(order)
            raise DomainError("reservation_expired", "The listing reservation expired. Start checkout again.", 409)
        intent = self.provider.create_intent(order_id=order.id, amount=order.total_amount, currency=order.currency, idempotency_key=idempotency_key)
        payment = Payment(
            order_id=order.id,
            provider=intent.provider,
            provider_reference=intent.provider_reference,
            amount=intent.amount,
            currency=intent.currency,
            status=PaymentStatus.PENDING,
            idempotency_key=idempotency_key,
        )
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def process_webhook(self, payload: PaymentWebhook, signature: str, expected_provider: str) -> Payment:
        settings = get_settings()
        if not settings.payment_webhook_secret:
            raise DomainError("payment_provider_unconfigured", "Payment webhooks are not configured.", 503)
        expected = hmac.new(settings.payment_webhook_secret.encode(), payload.model_dump_json().encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise DomainError("invalid_webhook_signature", "Webhook signature is invalid.", 401)
        payment = self.session.scalar(select(Payment).where(Payment.provider_reference == payload.provider_reference).with_for_update())
        if payment is None:
            raise DomainError("payment_not_found", "Payment was not found.", 404)
        if payment.provider != expected_provider:
            raise DomainError("provider_mismatch", "Payment provider did not match the webhook path.", 400)
        duplicate = self.session.scalar(select(PaymentEvent.id).where(PaymentEvent.provider == payment.provider, PaymentEvent.provider_event_id == payload.event_id))
        if duplicate:
            return payment
        order = self.session.scalar(select(Order).where(Order.id == payment.order_id).with_for_update())
        event = PaymentEvent(payment_id=payment.id, provider=payment.provider, provider_event_id=payload.event_id, event_type=payload.event_type)
        self.session.add(event)
        if payload.status == "succeeded":
            payment.status = PaymentStatus.SUCCEEDED
            order.status = OrderStatus.PAID
            order.reservation_expires_at = None
        elif payload.status == "failed":
            payment.status = PaymentStatus.FAILED
            order.status = OrderStatus.CANCELLED
            self._release_listing(order.listing_id)
        else:
            payment.status = PaymentStatus.REFUNDED
            order.status = OrderStatus.REFUNDED
            self._release_listing(order.listing_id)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def _release_expired(self, order: Order) -> None:
        order.status = OrderStatus.CANCELLED
        self._release_listing(order.listing_id)
        self.session.commit()

    def _release_listing(self, listing_id: UUID) -> None:
        listing = self.session.get(Listing, listing_id)
        if listing and listing.status == ListingStatus.RESERVED:
            listing.status = ListingStatus.ACTIVE
