from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from ..database import get_db
from ..models.models import TrackHistory, Listener, User
from ..schemas import StreamStatus, PlaylistTrack, PlaylistResponse, TrackHistoryResponse
from ..services.icecast import icecast_service
from ..services.auth import get_current_active_user
from ..config import MEDIA_DIR, PLAYLIST_FILE

router = APIRouter(prefix="/api/stream", tags=["stream"])


@router.get("/status", response_model=StreamStatus)
async def get_stream_status(db: Session = Depends(get_db)):
    """Get current stream status including listener count and current track."""
    stats = await icecast_service.get_stats()

    # Try to get current track from database
    current_track = db.query(TrackHistory).order_by(
        TrackHistory.played_at.desc()
    ).first()

    return StreamStatus(
        status=stats.get("status", "unknown"),
        listeners=stats.get("listeners", 0),
        current_track=TrackHistoryResponse(
            id=current_track.id,
            title=current_track.title,
            artist=current_track.artist,
            filename=current_track.filename,
            played_at=current_track.played_at,
        ) if current_track else None,
        bitrate=stats.get("bitrate"),
        format="MP3",
    )


@router.get("/listeners")
async def get_listener_count():
    """Get current listener count."""
    count = await icecast_service.get_listener_count()
    return {"listeners": count}


@router.get("/playlist", response_model=PlaylistResponse)
def get_playlist():
    """Get the current playlist from the playlist file."""
    tracks = []

    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    filename = os.path.basename(line)
                    title = filename.replace('.mp3', '').replace('_', ' ').title()
                    # Try to extract artist from filename if formatted as "Artist - Title.mp3"
                    artist = "Unknown"
                    if " - " in title:
                        parts = title.split(" - ", 1)
                        artist = parts[0].strip()
                        title = parts[1].strip()

                    tracks.append(PlaylistTrack(
                        id=i,
                        filename=filename,
                        title=title,
                        artist=artist,
                        duration=None,
                    ))

    return PlaylistResponse(tracks=tracks, total=len(tracks))


@router.post("/playlist/rebuild")
def rebuild_playlist(db: Session = Depends(get_db)):
    """Rebuild playlist from media directory."""
    if not os.path.exists(MEDIA_DIR):
        raise HTTPException(status_code=404, detail="Media directory not found")

    mp3_files = sorted([f for f in os.listdir(MEDIA_DIR) if f.endswith('.mp3')])

    with open(PLAYLIST_FILE, 'w', encoding='utf-8') as f:
        for mp3 in mp3_files:
            f.write(os.path.join(MEDIA_DIR, mp3) + "\n")

    return {"message": "Playlist rebuilt", "total": len(mp3_files)}


@router.get("/history", response_model=List[TrackHistoryResponse])
def get_track_history(
    skip: int = 0,
    limit: int = 50,
    episode_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get track playback history."""
    query = db.query(TrackHistory)

    if episode_id:
        query = query.filter(TrackHistory.episode_id == episode_id)

    tracks = query.order_by(TrackHistory.played_at.desc()).offset(skip).limit(limit).all()
    return tracks


@router.post("/history")
def add_track_history(
    title: str,
    artist: Optional[str] = None,
    filename: Optional[str] = None,
    episode_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a track to history (host or admin only)."""
    if current_user.role not in ["host", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    track = TrackHistory(
        title=title,
        artist=artist,
        filename=filename,
        episode_id=episode_id,
    )
    db.add(track)
    db.commit()
    db.refresh(track)

    return {"message": "Track added", "id": track.id}


@router.post("/listeners/heartbeat")
def listener_heartbeat(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Update listener heartbeat to keep session alive."""
    listener = db.query(Listener).filter(Listener.session_id == session_id).first()

    if listener:
        listener.is_active = True
        listener.last_ping = func.now()
    else:
        listener = Listener(
            session_id=session_id,
            is_active=True,
        )
        db.add(listener)

    db.commit()
    return {"message": "OK"}
