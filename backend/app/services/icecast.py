import httpx
import xml.etree.ElementTree as ET
from typing import Optional
from ..config import ICECAST_URL, ICECAST_ADMIN_PASSWORD


class IcecastService:
    def __init__(self):
        self.base_url = ICECAST_URL
        self.admin_password = ICECAST_ADMIN_PASSWORD

    async def get_stats(self) -> dict:
        """Get Icecast statistics including listener count and current track."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/admin/stats",
                    auth=("admin", self.admin_password)
                )

                if response.status_code == 200:
                    return self._parse_stats_xml(response.text)
                return self._default_stats()
        except Exception:
            return self._default_stats()

    def _parse_stats_xml(self, xml_content: str) -> dict:
        """Parse Icecast stats XML response."""
        try:
            root = ET.fromstring(xml_content)
            source = root.find(".//source")

            if source is not None:
                listeners = source.find("listeners")
                title_elem = source.find("title")
                genre = source.find("genre")
                bitrate = source.find("bitrate")

                return {
                    "status": "broadcasting" if listeners is not None else "offline",
                    "listeners": int(listeners.text) if listeners is not None else 0,
                    "current_track": title_elem.text if title_elem is not None else None,
                    "bitrate": int(bitrate.text) if bitrate is not None else None,
                    "genre": genre.text if genre is not None else None,
                }
        except Exception:
            pass

        return self._default_stats()

    def _default_stats(self) -> dict:
        """Return default stats when Icecast is unreachable."""
        return {
            "status": "unknown",
            "listeners": 0,
            "current_track": None,
            "bitrate": None,
            "genre": None,
        }

    async def get_listener_count(self) -> int:
        """Get current listener count."""
        stats = await self.get_stats()
        return stats.get("listeners", 0)

    async def get_current_track(self) -> Optional[str]:
        """Get the current playing track title."""
        stats = await self.get_stats()
        return stats.get("current_track")


icecast_service = IcecastService()
