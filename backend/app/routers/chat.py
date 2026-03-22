from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from ..database import get_db
from ..models.models import ChatMessage, Episode, User, MessageType
from ..schemas import ChatMessageCreate, ChatMessageResponse
from ..services.auth import get_current_active_user

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/episode/{episode_id}", response_model=List[ChatMessageResponse])
def get_episode_messages(
    episode_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get chat messages for an episode."""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    messages = db.query(ChatMessage).filter(
        ChatMessage.episode_id == episode_id
    ).order_by(ChatMessage.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for msg in messages:
        resp = ChatMessageResponse(
            id=msg.id,
            episode_id=msg.episode_id,
            user_id=msg.user_id,
            message=msg.message,
            message_type=msg.message_type,
            created_at=msg.created_at,
        )
        if msg.user:
            resp.username = msg.user.username
            resp.display_name = msg.user.display_name
        result.append(resp)

    return list(reversed(result))


@router.post("", response_model=ChatMessageResponse)
def create_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send a chat message to an episode."""
    episode = db.query(Episode).filter(Episode.id == message.episode_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    if episode.status != "live":
        raise HTTPException(status_code=400, detail="Can only send messages to live episodes")

    db_message = ChatMessage(
        episode_id=message.episode_id,
        user_id=current_user.id,
        message=message.message,
        message_type=MessageType.TEXT,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return ChatMessageResponse(
        id=db_message.id,
        episode_id=db_message.episode_id,
        user_id=db_message.user_id,
        message=db_message.message,
        message_type=db_message.message_type,
        created_at=db_message.created_at,
        username=current_user.username,
        display_name=current_user.display_name,
    )


@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a chat message (owner or admin only)."""
    db_message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")

    episode = db.query(Episode).filter(Episode.id == db_message.episode_id).first()

    if (current_user.role != "admin" and
        episode.host_id != current_user.id and
        db_message.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(db_message)
    db.commit()
    return {"message": "Message deleted"}
