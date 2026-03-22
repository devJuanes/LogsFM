# Radio Backend - FastAPI

Backend API para la plataforma de radio logsfm.com.

## Estructura

```
app/
├── __init__.py
├── main.py           # FastAPI application
├── config.py         # Configuration
├── database.py       # Database connection
├── schemas.py        # Pydantic schemas
├── models/
│   ├── __init__.py
│   └── models.py     # SQLAlchemy models
├── routers/
│   ├── __init__.py
│   ├── auth.py       # Authentication endpoints
│   ├── episodes.py    # Episode management
│   ├── chat.py       # Chat messages
│   ├── participation.py  # Participation requests
│   ├── stream.py      # Stream/playlist management
│   └── websocket.py   # WebSocket endpoints
└── services/
    ├── __init__.py
    ├── auth.py       # Authentication utilities
    └── icecast.py    # Icecast integration
```

## Instalación

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Crear base de datos PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE radio_db;"
sudo -u postgres psql -c "CREATE USER radio WITH PASSWORD 'RadioPass123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE radio_db TO radio;"

# Crear tablas (automático al iniciar)
# O manualmente: psql -U radio -d radio_db -f schema.sql

# Ejecutar
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints API

### Autenticación
- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Login (OAuth2 password flow)
- `GET /api/auth/me` - Usuario actual

### Episodios
- `GET /api/episodes` - Listar episodios
- `GET /api/episodes/{id}` - Detalle de episodio
- `POST /api/episodes` - Crear episodio
- `PUT /api/episodes/{id}` - Actualizar episodio
- `DELETE /api/episodes/{id}` - Eliminar episodio
- `POST /api/episodes/{id}/start` - Iniciar episodio
- `POST /api/episodes/{id}/end` - Terminar episodio

### Chat
- `GET /api/chat/episode/{id}` - Mensajes de episodio
- `POST /api/chat` - Enviar mensaje
- `DELETE /api/chat/{id}` - Eliminar mensaje

### Participación
- `GET /api/participation/episode/{id}` - Solicitudes de episodio
- `POST /api/participation` - Crear solicitud
- `PUT /api/participation/{id}` - Actualizar estado
- `DELETE /api/participation/{id}` - Eliminar solicitud

### Stream
- `GET /api/stream/status` - Estado del stream
- `GET /api/stream/listeners` - Número de oyentes
- `GET /api/stream/playlist` - Playlist actual
- `POST /api/stream/playlist/rebuild` - Reconstruir playlist
- `GET /api/stream/history` - Historial de tracks

### WebSocket
- `WS /ws/chat/{episode_id}` - Chat en vivo
- `WS /ws/listeners` - Actualizaciones de oyentes

## Desarrollo

```bash
# Con Docker (usando docker-compose del proyecto padre)
docker-compose up backend

# Directamente
python -m uvicorn app.main:app --reload
```

## Producción

```bash
# Usar systemd - crear /etc/systemd/system/radio-backend.service
[Unit]
Description=Radio Backend API
After=network.target postgresql.service

[Service]
User=radio
WorkingDirectory=/home/radio/radio-backend
EnvironmentFile=/home/radio/radio-backend/.env
ExecStart=/home/radio/radio-backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```
