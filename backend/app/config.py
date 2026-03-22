import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://radio:RadioPass123@localhost:5432/radio_db"
)

ICECAST_URL = os.getenv("ICECAST_URL", "http://localhost:8000")
ICECAST_ADMIN_PASSWORD = os.getenv("ICECAST_ADMIN_PASSWORD", "hackme")
ICECAST_SOURCE_PASSWORD = os.getenv("ICECAST_SOURCE_PASSWORD", "hackme")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

MEDIA_DIR = os.getenv("MEDIA_DIR", "/var/lib/icecast2/media/")
PLAYLIST_FILE = os.getenv("PLAYLIST_FILE", "/var/lib/icecast2/playlist.txt")
