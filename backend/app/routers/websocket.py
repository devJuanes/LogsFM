from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Set
from datetime import datetime, timezone
import json
import asyncio
from ..database import get_db, SessionLocal
from ..models.models import ChatMessage, Episode, Listener, User, MessageType
from ..services.auth import verify_password, get_password_hash
from ..schemas import ChatMessageResponse

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        # episode_id -> list of websocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # websocket -> (episode_id, user_info)
        self.connection_info: Dict[WebSocket, tuple] = {}
        # listener websockets
        self.listener_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, episode_id: int, user_info: dict = None):
        await websocket.accept()
        if episode_id not in self.active_connections:
            self.active_connections[episode_id] = []
        self.active_connections[episode_id].append(websocket)
        self.connection_info[websocket] = (episode_id, user_info)

    def disconnect(self, websocket: WebSocket):
        info = self.connection_info.get(websocket)
        if info:
            episode_id, _ = info
            if episode_id in self.active_connections:
                if websocket in self.active_connections[episode_id]:
                    self.active_connections[episode_id].remove(websocket)
            del self.connection_info[websocket]

    async def broadcast_to_episode(self, episode_id: int, message: dict):
        if episode_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[episode_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)

            for conn in disconnected:
                self.disconnect(conn)

    async def broadcast_listeners(self, count: int):
        disconnected = []
        for connection in self.listener_connections:
            try:
                await connection.send_json({"type": "listeners", "count": count})
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.listener_connections.discard(conn)


manager = ConnectionManager()


@router.websocket("/ws/chat/{episode_id}")
async def websocket_chat(
    websocket: WebSocket,
    episode_id: int,
    token: str = Query(None),
):
    """WebSocket endpoint for live chat in an episode."""
    # Authenticate user if token provided
    user_info = None
    if token:
        try:
            from jose import jwt
            from ..config import SECRET_KEY, ALGORITHM
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user and user.is_active:
                        user_info = {
                            "id": user.id,
                            "username": user.username,
                            "display_name": user.display_name,
                            "role": user.role,
                        }
                finally:
                    db.close()
        except Exception:
            pass

    await manager.connect(websocket, episode_id, user_info)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "episode_id": episode_id,
            "user": user_info,
        })

        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)

                if message_data.get("type") == "message":
                    msg_content = message_data.get("content", "").strip()
                    if not msg_content:
                        continue

                    # Save to database
                    db = SessionLocal()
                    try:
                        db_message = ChatMessage(
                            episode_id=episode_id,
                            user_id=user_info["id"] if user_info else None,
                            message=msg_content,
                            message_type=MessageType.TEXT,
                        )
                        db.add(db_message)
                        db.commit()
                        db.refresh(db_message)

                        response = {
                            "type": "message",
                            "id": db_message.id,
                            "content": db_message.message,
                            "user_id": db_message.user_id,
                            "username": user_info.get("username") if user_info else "Anonymous",
                            "display_name": user_info.get("display_name") if user_info else "Anonymous",
                            "created_at": db_message.created_at.isoformat(),
                        }
                        await manager.broadcast_to_episode(episode_id, response)
                    finally:
                        db.close()

                elif message_data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/listeners")
async def websocket_listeners(websocket: WebSocket):
    """WebSocket endpoint for real-time listener count updates."""
    await websocket.accept()
    manager.listener_connections.add(websocket)

    try:
        # Send initial connection message
        await websocket.send_json({"type": "connected"})

        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                if message_data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.listener_connections.discard(websocket)
