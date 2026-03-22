        """
        Radio Backend - API para gestionar playlist MP3
        Backend: FastAPI
        Streaming: Icecast + Ezstream
        """

        from fastapi import FastAPI, HTTPException, Query
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        from typing import Optional
        import json
        import os
        from datetime import datetime

        app = FastAPI(title="Radio API", version="1.0.0")

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Rutas
        PLAYLIST_FILE = "/var/lib/icecast2/playlist.txt"
        MEDIA_DIR = "/var/lib/icecast2/media/"
        CONFIG_FILE = "config.json"

        # Modelos
        class Track(BaseModel):
            id: int
            title: str
            artist: str
            filename: str
            duration: Optional[int] = None

        class TrackCreate(BaseModel):
            title: str
            artist: str
            filename: str

        # Rutas API
        @app.get("/")
        def root():
            return {"status": "ok", "radio": "Radio API", "version": "1.0.0"}

        @app.get("/status")
        def status():
            """Estado actual de la radio"""
            return {
                "status": "broadcasting",
                "listeners": 0,  # Se puede integrar con Icecast API
                "current_track": None,
                "next_track": None
            }

        @app.get("/playlist")
        def get_playlist():
            """Obtener lista de reproducción"""
            tracks = []
            if os.path.exists(PLAYLIST_FILE):
                with open(PLAYLIST_FILE, 'r') as f:
                    for i, line in enumerate(f, 1):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            filename = os.path.basename(line)
                            title = filename.replace('.mp3', '').replace('_', ' ').title()
                            tracks.append({
                                "id": i,
                                "filename": filename,
                                "title": title,
                                "artist": "Unknown"
                            })
            return {"tracks": tracks, "total": len(tracks)}

        @app.post("/playlist")
        def add_track(track: TrackCreate):
            """Agregar tema a la playlist"""
            # Crear directorio si no existe
            os.makedirs(MEDIA_DIR, exist_ok=True)

            filepath = os.path.join(MEDIA_DIR, track.filename)
            if not os.path.exists(filepath):
                raise HTTPException(status_code=404, detail="Archivo no encontrado")

            # Agregar a playlist
            with open(PLAYLIST_FILE, 'a') as f:
                f.write(f"{filepath}\n")

            return {"message": "Tema agregado", "track": track}

        @app.delete("/playlist/{track_id}")
        def remove_track(track_id: int):
            """Eliminar tema de la playlist"""
            if not os.path.exists(PLAYLIST_FILE):
                raise HTTPException(status_code=404, detail="Playlist no encontrada")

            with open(PLAYLIST_FILE, 'r') as f:
                lines = f.readlines()

            if track_id < 1 or track_id > len(lines):
                raise HTTPException(status_code=404, detail="Tema no encontrado")

            removed = lines.pop(track_id - 1)

            with open(PLAYLIST_FILE, 'w') as f:
                f.writelines(lines)

            return {"message": "Tema eliminado", "removed": removed.strip()}

        @app.post("/playlist/rebuild")
        def rebuild_playlist():
            """Reconstruir playlist desde los archivos en media/"""
            if not os.path.exists(MEDIA_DIR):
                raise HTTPException(status_code=404, detail="Directorio media no encontrado")

            mp3_files = sorted([f for f in os.listdir(MEDIA_DIR) if f.endswith('.mp3')])

            with open(PLAYLIST_FILE, 'w') as f:
                for mp3 in mp3_files:
                    f.write(os.path.join(MEDIA_DIR, mp3) + "\n")

            return {"message": "Playlist reconstruida", "total": len(mp3_files)}


        if __name__ == "__main__":
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8000)
