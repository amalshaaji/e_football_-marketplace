from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from app.auth.service import AuthService, refresh_pair, token_pair
from app.core.dependencies import get_db
from app.database.models import User

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    return token_pair(AuthService(db).register(payload))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    return token_pair(AuthService(db).authenticate(payload))


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    return refresh_pair(db, payload.refresh_token)


@router.post("/logout", status_code=204)
def logout(current_user: Annotated[User, Depends(get_current_user)]) -> Response:
    # Short lived access tokens and client-side token disposal provide logout
    # until server-side refresh-token revocation is added.
    return Response(status_code=204)


@router.get("/me", response_model=UserResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    return {"id": str(current_user.id), "email": current_user.email, "role": current_user.role.value, "display_name": current_user.profile.display_name if current_user.profile else ""}
