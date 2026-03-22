from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    HOST = "host"
    ADMIN = "admin"


class EpisodeStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    ENDED = "ended"
    CANCELLED = "cancelled"


class ParticipationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class MessageType(str, Enum):
    TEXT = "text"
    SYSTEM = "system"
    HOST = "host"


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    display_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# Episode schemas
class EpisodeBase(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_start: datetime
    scheduled_end: datetime


class EpisodeCreate(EpisodeBase):
    pass


class EpisodeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    status: Optional[EpisodeStatus] = None


class EpisodeResponse(EpisodeBase):
    id: int
    host_id: int
    status: EpisodeStatus
    stream_url: Optional[str] = None
    created_at: datetime
    host: Optional[UserResponse] = None

    class Config:
        from_attributes = True


# Participation schemas
class ParticipationRequestBase(BaseModel):
    message: Optional[str] = None


class ParticipationRequestCreate(ParticipationRequestBase):
    episode_id: int


class ParticipationRequestUpdate(BaseModel):
    status: ParticipationStatus


class ParticipationRequestResponse(BaseModel):
    id: int
    episode_id: int
    user_id: int
    message: Optional[str]
    status: ParticipationStatus
    created_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


# Chat schemas
class ChatMessageBase(BaseModel):
    message: str


class ChatMessageCreate(ChatMessageBase):
    episode_id: int


class ChatMessageResponse(BaseModel):
    id: int
    episode_id: int
    user_id: Optional[int]
    message: str
    message_type: MessageType
    created_at: datetime
    username: Optional[str] = None
    display_name: Optional[str] = None

    class Config:
        from_attributes = True


# Stream/Track schemas
class TrackHistoryResponse(BaseModel):
    id: int
    title: str
    artist: Optional[str]
    filename: Optional[str]
    played_at: datetime

    class Config:
        from_attributes = True


class StreamStatus(BaseModel):
    status: str
    listeners: int
    current_track: Optional[TrackHistoryResponse] = None
    bitrate: Optional[int] = None
    format: Optional[str] = None


class PlaylistTrack(BaseModel):
    id: int
    filename: str
    title: str
    artist: str
    duration: Optional[int] = None


class PlaylistResponse(BaseModel):
    tracks: List[PlaylistTrack]
    total: int
