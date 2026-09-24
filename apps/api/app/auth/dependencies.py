from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.errors import DomainError
from app.auth.security import decode_token
from app.database.models import User, UserRole

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise DomainError("authentication_required", "Sign in to continue.", 401)
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise DomainError("invalid_token", "Your session is invalid or expired.", 401) from exc
    user = db.get(User, UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise DomainError("invalid_token", "Your session is invalid or expired.", 401)
    return user


def require_roles(*roles: UserRole):
    def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in roles:
            raise DomainError("permission_denied", "You do not have permission to perform this action.", 403)
        return user

    return dependency
