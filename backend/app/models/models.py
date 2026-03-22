from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class UserRole(str, enum.Enum):
    USER = "user"
    HOST = "host"
    ADMIN = "admin"


class EpisodeStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    ENDED = "ended"
    CANCELLED = "cancelled"


class ParticipationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class MessageType(str, enum.Enum):
    TEXT = "text"
    SYSTEM = "system"
    HOST = "host"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    episodes = relationship("Episode", back_populates="host")
    participation_requests = relationship("ParticipationRequest", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(EpisodeStatus), default=EpisodeStatus.SCHEDULED)
    stream_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    host = relationship("User", back_populates="episodes")
    participation_requests = relationship("ParticipationRequest", back_populates="episode")
    chat_messages = relationship("ChatMessage", back_populates="episode")


class ParticipationRequest(Base):
    __tablename__ = "participation_requests"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=True)
    status = Column(SQLEnum(ParticipationStatus), default=ParticipationStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    episode = relationship("Episode", back_populates="participation_requests")
    user = relationship("User", back_populates="participation_requests")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    message = Column(Text, nullable=False)
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    episode = relationship("Episode", back_populates="chat_messages")
    user = relationship("User", back_populates="chat_messages")


class Listener(Base):
    __tablename__ = "listeners"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    last_ping = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TrackHistory(Base):
    __tablename__ = "track_history"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    artist = Column(String(200), nullable=True)
    filename = Column(String(500), nullable=True)
    played_at = Column(DateTime(timezone=True), server_default=func.now())
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=True)
