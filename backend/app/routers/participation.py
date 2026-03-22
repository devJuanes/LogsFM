from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.models import ParticipationRequest, Episode, User, ParticipationStatus
from ..schemas import ParticipationRequestCreate, ParticipationRequestUpdate, ParticipationRequestResponse
from ..services.auth import get_current_active_user

router = APIRouter(prefix="/api/participation", tags=["participation"])


@router.get("/episode/{episode_id}", response_model=List[ParticipationRequestResponse])
def get_episode_requests(
    episode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all participation requests for an episode (host or admin only)."""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    if current_user.role != "admin" and episode.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the host or admin can view requests")

    requests = db.query(ParticipationRequest).filter(
        ParticipationRequest.episode_id == episode_id
    ).all()

    result = []
    for req in requests:
        resp = ParticipationRequestResponse(
            id=req.id,
            episode_id=req.episode_id,
            user_id=req.user_id,
            message=req.message,
            status=req.status,
            created_at=req.created_at,
        )
        if req.user:
            resp.user = {
                "id": req.user.id,
                "username": req.user.username,
                "display_name": req.user.display_name,
                "role": req.user.role,
            }
        result.append(resp)
    return result


@router.post("", response_model=ParticipationRequestResponse)
def create_request(
    request: ParticipationRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a participation request for an episode."""
    episode = db.query(Episode).filter(Episode.id == request.episode_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    if episode.status != "scheduled":
        raise HTTPException(status_code=400, detail="Can only request participation for scheduled episodes")

    # Check if user already has a pending request
    existing = db.query(ParticipationRequest).filter(
        ParticipationRequest.episode_id == request.episode_id,
        ParticipationRequest.user_id == current_user.id,
        ParticipationRequest.status == ParticipationStatus.PENDING
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="You already have a pending request")

    db_request = ParticipationRequest(
        episode_id=request.episode_id,
        user_id=current_user.id,
        message=request.message,
        status=ParticipationStatus.PENDING,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    return ParticipationRequestResponse(
        id=db_request.id,
        episode_id=db_request.episode_id,
        user_id=db_request.user_id,
        message=db_request.message,
        status=db_request.status,
        created_at=db_request.created_at,
    )


@router.put("/{request_id}", response_model=ParticipationRequestResponse)
def update_request(
    request_id: int,
    update: ParticipationRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a participation request status (host or admin only)."""
    db_request = db.query(ParticipationRequest).filter(ParticipationRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")

    episode = db.query(Episode).filter(Episode.id == db_request.episode_id).first()
    if current_user.role != "admin" and episode.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the host or admin can update requests")

    db_request.status = update.status
    db.commit()
    db.refresh(db_request)

    return ParticipationRequestResponse(
        id=db_request.id,
        episode_id=db_request.episode_id,
        user_id=db_request.user_id,
        message=db_request.message,
        status=db_request.status,
        created_at=db_request.created_at,
    )


@router.delete("/{request_id}")
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a participation request (owner, host, or admin)."""
    db_request = db.query(ParticipationRequest).filter(ParticipationRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")

    episode = db.query(Episode).filter(Episode.id == db_request.episode_id).first()

    if (current_user.role != "admin" and
        episode.host_id != current_user.id and
        db_request.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(db_request)
    db.commit()
    return {"message": "Request deleted"}
