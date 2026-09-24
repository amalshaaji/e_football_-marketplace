import logging
import hashlib
import json
from email.message import EmailMessage
from pathlib import Path
import smtplib
import ssl
import struct
from datetime import UTC, datetime

from sqlalchemy import select

from app.database.models import Listing, ListingStatus, Notification, Order, OrderStatus
from app.database.session import SessionLocal
from app.core.config import get_settings

logger = logging.getLogger("marketplace.jobs")


class JobNotConfigured(RuntimeError):
    """Raised when a job requires a provider not configured in this deployment."""


def persist_notification(payload: dict) -> None:
    with SessionLocal() as session:
        session.add(Notification(user_id=payload["user_id"], event_type=payload["event_type"], payload=payload.get("payload", {})))
        session.commit()


def expire_reservations(_payload: dict) -> None:
    now = datetime.now(UTC)
    with SessionLocal() as session:
        orders = list(session.scalars(select(Order).where(Order.status == OrderStatus.PAYMENT_PENDING, Order.reservation_expires_at <= now).with_for_update(skip_locked=True)))
        for order in orders:
            order.status = OrderStatus.CANCELLED
            listing = session.get(Listing, order.listing_id)
            if listing and listing.status == ListingStatus.RESERVED:
                listing.status = ListingStatus.ACTIVE
        session.commit()
        logger.info("expired checkout reservations count=%d", len(orders))


def send_email(payload: dict) -> None:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_from_email:
        raise JobNotConfigured("SMTP email provider is not configured")
    message = EmailMessage()
    message["From"] = settings.smtp_from_email
    message["To"] = payload["to"]
    message["Subject"] = payload["subject"]
    message.set_content(payload["body"])
    context = ssl.create_default_context()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as client:
        if settings.smtp_use_tls:
            client.starttls(context=context)
        if settings.smtp_username:
            client.login(settings.smtp_username, settings.smtp_password)
        client.send_message(message)


def process_image(payload: dict) -> None:
    root = Path(get_settings().media_root).resolve()
    source = (root / payload["path"]).resolve()
    if root not in source.parents or not source.is_file():
        raise ValueError("Image path is outside MEDIA_ROOT or does not exist")
    raw = source.read_bytes()
    width, height, image_format = _read_image_dimensions(raw)
    metadata = {
        "source": source.name,
        "format": image_format,
        "width": width,
        "height": height,
        "size_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    metadata_path = source.with_suffix(source.suffix + ".metadata.json")
    metadata_path.write_text(json.dumps(metadata, separators=(",", ":")), encoding="utf-8")
    logger.info("image metadata processed path=%s width=%d height=%d", source.name, width, height)


def _read_image_dimensions(raw: bytes) -> tuple[int, int, str]:
    if raw.startswith(b"\x89PNG\r\n\x1a\n") and len(raw) >= 24:
        width, height = struct.unpack(">II", raw[16:24])
        if width and height:
            return width, height, "PNG"
    if raw.startswith((b"GIF87a", b"GIF89a")) and len(raw) >= 10:
        width, height = struct.unpack("<HH", raw[6:10])
        if width and height:
            return width, height, "GIF"
    if raw.startswith(b"\xff\xd8"):
        offset = 2
        while offset + 9 < len(raw):
            if raw[offset] != 0xFF:
                offset += 1
                continue
            marker = raw[offset + 1]
            offset += 2
            if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
                continue
            length = int.from_bytes(raw[offset : offset + 2], "big")
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                height, width = struct.unpack(">HH", raw[offset + 3 : offset + 7])
                if width and height:
                    return width, height, "JPEG"
            offset += length
    raise ValueError("Image format is unsupported or the file is invalid")


HANDLERS = {
    "notification.persist": persist_notification,
    "orders.expire_reservations": expire_reservations,
    "email.send": send_email,
    "image.process": process_image,
}
