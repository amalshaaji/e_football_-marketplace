from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest, RegisterRequest
from app.auth.security import create_token, decode_token, hash_password, verify_password
from app.core.errors import DomainError
from app.database.models import User, UserProfile, UserRole


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def register(self, payload: RegisterRequest) -> User:
        email = str(payload.email).strip().lower()
        if self.session.scalar(select(User.id).where(User.email == email)):
            raise DomainError("email_in_use", "An account with this email already exists.", 409)
        user = User(email=email, password_hash=hash_password(payload.password), role=UserRole.BUYER)
        user.profile = UserProfile(display_name=payload.display_name.strip())
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def authenticate(self, payload: LoginRequest) -> User:
        email = str(payload.email).strip().lower()
        user = self.session.scalar(select(User).where(User.email == email))
        if user is None or not verify_password(payload.password, user.password_hash) or not user.is_active:
            raise DomainError("invalid_credentials", "Email or password is incorrect.", 401)
        return user


def token_pair(user: User) -> dict:
    from app.core.config import get_settings

    settings = get_settings()
    access_seconds = settings.access_token_expire_minutes * 60
    refresh_seconds = settings.refresh_token_expire_days * 24 * 60 * 60
    access = create_token(user.id, user.role.value, token_type="access", expires_in=access_seconds)
    refresh = create_token(user.id, user.role.value, token_type="refresh", expires_in=refresh_seconds)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "expires_in": access_seconds,
        "user": {"id": str(user.id), "email": user.email, "role": user.role.value, "display_name": user.profile.display_name if user.profile else ""},
    }


def refresh_pair(session: Session, refresh_token: str) -> dict:
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
        user = session.get(User, UUID(payload["sub"]))
    except (ValueError, KeyError) as exc:
        raise DomainError("invalid_refresh_token", "Your refresh session is invalid or expired.", 401) from exc
    if user is None or not user.is_active:
        raise DomainError("invalid_refresh_token", "Your refresh session is invalid or expired.", 401)
    return token_pair(user)
