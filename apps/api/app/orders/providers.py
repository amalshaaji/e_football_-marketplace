from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class PaymentIntent:
    provider: str
    provider_reference: str
    amount: Decimal
    currency: str
    checkout_url: str | None = None


class PaymentProvider(Protocol):
    name: str

    def create_intent(self, *, order_id: UUID, amount: Decimal, currency: str, idempotency_key: str) -> PaymentIntent: ...


class UnconfiguredProvider:
    """Local placeholder that never represents or verifies a real charge."""
    name = "unconfigured"

    def create_intent(self, *, order_id: UUID, amount: Decimal, currency: str, idempotency_key: str) -> PaymentIntent:
        return PaymentIntent(self.name, f"pending-{order_id}", amount, currency)
