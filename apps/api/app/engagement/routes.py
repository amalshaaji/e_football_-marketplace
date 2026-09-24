from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.core.dependencies import get_db
from app.database.models import Message, Notification, Report, Review, User, UserRole
from app.engagement.schemas import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse, NotificationResponse, ReportCreate, ReviewCreate, ReviewResponse
from app.engagement.service import EngagementService

router = APIRouter()


@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(payload: ReviewCreate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> Review:
    return EngagementService(db).create_review(user, payload)


@router.get("/reviews", response_model=list[ReviewResponse])
def seller_reviews(seller_id: UUID = Query(), db: Session = Depends(get_db)) -> list[Review]:
    return EngagementService(db).list_reviews(seller_id)


@router.patch("/reviews/{review_id}/moderation", response_model=ReviewResponse)
def moderate_review(review_id: UUID, hidden: bool, admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))], db: Annotated[Session, Depends(get_db)]) -> Review:
    return EngagementService(db).moderate_review(review_id, hidden, admin)


@router.post("/reports", status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    report = EngagementService(db).create_report(user, payload)
    return {"id": str(report.id), "status": report.status.value, "created_at": report.created_at}


@router.get("/notifications", response_model=list[NotificationResponse])
def list_notifications(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> list[Notification]:
    return EngagementService(db).list_notifications(user)


@router.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(notification_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> Notification:
    return EngagementService(db).mark_notification_read(notification_id, user)


def _conversation_response(conversation, db: Session) -> dict:
    messages = list(db.scalars(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at.asc())))
    return {
        "id": conversation.id,
        "buyer_id": conversation.buyer_id,
        "seller_id": conversation.seller_id,
        "listing_id": conversation.listing_id,
        "created_at": conversation.created_at,
        "messages": messages,
    }


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def open_conversation(payload: ConversationCreate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    conversation = EngagementService(db).open_conversation(user, payload)
    return _conversation_response(conversation, db)


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> list[dict]:
    return [_conversation_response(item, db) for item in EngagementService(db).list_conversations(user)]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def conversation_detail(conversation_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> dict:
    conversation = EngagementService(db).get_conversation(conversation_id, user)
    return _conversation_response(conversation, db)


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
def send_message(conversation_id: UUID, payload: MessageCreate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> Message:
    return EngagementService(db).send_message(conversation_id, user, payload)
