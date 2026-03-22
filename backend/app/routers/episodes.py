from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from ..database import get_db
from ..models.models import Episode, User, EpisodeStatus
from ..schemas import EpisodeCreate, EpisodeUpdate, EpisodeResponse
from ..services.auth import get_current_active_user

router = APIRouter(prefix="/api/episodes", tags=["episodes"])


def episode_to_response(episode: Episode, include_host: bool = False) -> dict:
    """Convert episode model to response dict."""
    response = {
        "id": episode.id,
        "title": episode.title,
        "description": episode.description,
        "host_id": episode.host_id,
        "scheduled_start": episode.scheduled_start,
        "scheduled_end": episode.scheduled_end,
        "status": episode.status,
        "stream_url": episode.stream_url,
        "created_at": episode.created_at,
    }
    if include_host and episode.host:
        response["host"] = {
            "id": episode.host.id,
            "username": episode.host.username,
            "display_name": episode.host.display_name,
            "role": episode.host.role,
        }
    return response


@router.get("", response_model=List[EpisodeResponse])
def get_episodes(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[EpisodeStatus] = None,
    upcoming: bool = False,
    db: Session = Depends(get_db),
):
    """Get all episodes, optionally filtered."""
    query = db.query(Episode)

    if status_filter:
        query = query.filter(Episode.status == status_filter)

    if upcoming:
        now = datetime.now(timezone.utc)
        query = query.filter(
            Episode.scheduled_start > now,
            Episode.status == EpisodeStatus.SCHEDULED
        )

    episodes = query.order_by(Episode.scheduled_start.desc()).offset(skip).limit(limit).all()
    return [episode_to_response(ep, include_host=True) for ep in episodes]


@router.get("/{episode_id}", response_model=EpisodeResponse)
def get_episode(episode_id: int, db: Session = Depends(get_db)):
    """Get a specific episode by ID."""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode_to_response(episode, include_host=True)


@router.post("", response_model=EpisodeResponse)
def create_episode(
    episode: EpisodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new episode (host or admin only)."""
    if current_user.role not in ["host", "admin"]:
        raise HTTPException(status_code=403, detail="Only hosts and admins can create episodes")

    db_episode = Episode(
        title=episode.title,
        description=episode.description,
        host_id=current_user.id,
        scheduled_start=episode.scheduled_start,
        scheduled_end=episode.scheduled_end,
        status=EpisodeStatus.SCHEDULED,
    )
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    return episode_to_response(db_episode, include_host=True)


@router.put("/{episode_id}", response_model=EpisodeResponse)
def update_episode(
    episode_id: int,
    episode_update: EpisodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an episode (owner host or admin only)."""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    if current_user.role != "admin" and episode.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = episode_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(episode, key, value)

    db.commit()
    db.refresh(episode)
    return episode_to_response(episode, include_host=True)


@router.delete("/{episode_id}")
def delete_episode(
    episode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an episode (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete episodes")

    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    db.delete(episode)
    db.commit()
    return {"message": "Episode deleted"}


@router.post("/{episode_id}/start")
def start_episode(
    episode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark episode as live (owner host or admin only)."""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    if current_user.role != "admin" and episode.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    episode.status = EpisodeStatus.LIVE
    db.commit()
    return {"message": "Episode started", "status": "live"}


@router.post("/{episode_id}/end")
def end_episode(
    episode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark episode as ended (owner host or admin only)."""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    if current_user.role != "admin" and episode.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    episode.status = EpisodeStatus.ENDED
    db.commit()
    return {"message": "Episode ended", "status": "ended"}
