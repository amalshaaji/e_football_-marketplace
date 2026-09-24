import base64
import hashlib
import hmac
import json
import secrets
import time
import uuid

from app.core.config import get_settings

_PBKDF2_ITERATIONS = 310_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${_b64(salt)}${_b64(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), _unb64(salt), int(iterations))
        return hmac.compare_digest(_b64(digest), expected)
    except (ValueError, TypeError):
        return False


def create_token(user_id: uuid.UUID, role: str, *, token_type: str, expires_in: int) -> str:
    now = int(time.time())
    payload = {"sub": str(user_id), "role": role, "type": token_type, "iat": now, "exp": now + expires_in, "jti": secrets.token_urlsafe(16)}
    encoded = _b64(json.dumps(payload, separators=(",", ":")).encode())
    signature = _sign(encoded)
    return f"{encoded}.{signature}"


def decode_token(token: str, *, expected_type: str = "access") -> dict:
    try:
        encoded, signature = token.split(".", 1)
        if not hmac.compare_digest(_sign(encoded), signature):
            raise ValueError("Invalid token signature")
        payload = json.loads(_unb64(encoded))
        if payload.get("type") != expected_type or int(payload["exp"]) <= int(time.time()):
            raise ValueError("Expired or wrong token type")
        uuid.UUID(payload["sub"])
        return payload
    except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid token") from exc


def _sign(value: str) -> str:
    secret = get_settings().auth_secret_key.encode()
    return _b64(hmac.new(secret, value.encode(), hashlib.sha256).digest())


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
