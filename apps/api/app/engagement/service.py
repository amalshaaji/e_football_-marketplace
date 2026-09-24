from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.database.models import Conversation, Listing, ListingStatus, Message, Notification, Order, OrderStatus, Review, User
from app.engagement.schemas import ConversationCreate, MessageCreate, ReviewCreate


class EngagementService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_review(self, author: User, payload: ReviewCreate) -> Review:
        order = self.session.get(Order, payload.order_id)
        if order is None or order.buyer_id != author.id:
            raise DomainError("order_not_reviewable", "Only the buyer can review this order.", 404)
        if order.status != OrderStatus.COMPLETED:
            raise DomainError("order_not_completed", "Reviews are available after order completion.", 409)
        review = Review(order_id=order.id, author_id=author.id, seller_id=order.seller_id, rating=payload.rating, body=payload.body)
        self.session.add(review)
        self.session.flush()
        self.session.add(Notification(user_id=order.seller_id, event_type="review.created", payload={"review_id": str(review.id), "order_id": str(order.id)}))
        self.session.commit()
        self.session.refresh(review)
        return review

    def list_reviews(self, seller_id: UUID) -> list[Review]:
        return list(self.session.scalars(select(Review).where(Review.seller_id == seller_id, Review.is_hidden.is_(False)).order_by(Review.created_at.desc())))

    def moderate_review(self, review_id: UUID, hide: bool) -> Review:
        review = self.session.get(Review, review_id)
        if review is None:
            raise DomainError("review_not_found", "Review was not found.", 404)
        review.is_hidden = hide
        self.session.commit()
        self.session.refresh(review)
        return review

    def open_conversation(self, buyer: User, payload: ConversationCreate) -> Conversation:
        listing = self.session.get(Listing, payload.listing_id)
        if listing is None or listing.status not in {ListingStatus.ACTIVE, ListingStatus.RESERVED, ListingStatus.SOLD}:
            raise DomainError("listing_unavailable", "This listing is unavailable for messaging.", 404)
        if listing.seller_id == buyer.id:
            raise DomainError("invalid_participant", "You cannot start a conversation with yourself.", 409)
        conversation = self.session.scalar(select(Conversation).where(Conversation.buyer_id == buyer.id, Conversation.seller_id == listing.seller_id, Conversation.listing_id == listing.id))
        if conversation is None:
            conversation = Conversation(buyer_id=buyer.id, seller_id=listing.seller_id, listing_id=listing.id)
            self.session.add(conversation)
            self.session.flush()
        self._add_message(conversation, buyer, MessageCreate(body=payload.body))
        return conversation

    def send_message(self, conversation_id: UUID, sender: User, payload: MessageCreate) -> Message:
        conversation = self._participant_conversation(conversation_id, sender)
        return self._add_message(conversation, sender, payload)

    def list_conversations(self, user: User) -> list[Conversation]:
        conversations = list(self.session.scalars(select(Conversation).where((Conversation.buyer_id == user.id) | (Conversation.seller_id == user.id)).order_by(Conversation.updated_at.desc())))
        for conversation in conversations:
            self._mark_read(conversation, user)
        self.session.commit()
        return conversations

    def get_conversation(self, conversation_id: UUID, user: User) -> Conversation:
        conversation = self._participant_conversation(conversation_id, user)
        self._mark_read(conversation, user)
        self.session.commit()
        return conversation

    def _participant_conversation(self, conversation_id: UUID, user: User) -> Conversation:
        conversation = self.session.get(Conversation, conversation_id)
        if conversation is None or user.id not in {conversation.buyer_id, conversation.seller_id}:
            raise DomainError("conversation_not_found", "Conversation was not found.", 404)
        return conversation

    def _add_message(self, conversation: Conversation, sender: User, payload: MessageCreate) -> Message:
        message = Message(conversation_id=conversation.id, sender_id=sender.id, body=payload.body.strip())
        recipient_id = conversation.seller_id if sender.id == conversation.buyer_id else conversation.buyer_id
        self.session.add(message)
        conversation.updated_at = datetime.now(UTC)
        self.session.flush()
        self.session.add(Notification(user_id=recipient_id, event_type="message.created", payload={"conversation_id": str(conversation.id), "message_id": str(message.id)}))
        self.session.commit()
        self.session.refresh(message)
        return message

    def _mark_read(self, conversation: Conversation, user: User) -> None:
        self.session.query(Message).filter(Message.conversation_id == conversation.id, Message.sender_id != user.id, Message.read_at.is_(None)).update({Message.read_at: datetime.now(UTC)}, synchronize_session=False)
