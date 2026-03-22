#!/bin/bash
# Script para regenerar la playlist automáticamente

MEDIA_DIR="/var/lib/icecast2/media"
PLAYLIST_FILE="/var/lib/icecast2/playlist.txt"

echo "Buscando archivos MP3 en $MEDIA_DIR..."
find "$MEDIA_DIR" -name "*.mp3" | sort > "$PLAYLIST_FILE"

COUNT=$(wc -l < "$PLAYLIST_FILE")
echo "Playlist actualizada con $COUNT temas."

if [ $COUNT -eq 0 ]; then
    echo "ADVERTENCIA: No se encontraron archivos MP3!"
    exit 1
fi

echo "Playlist:"
cat "$PLAYLIST_FILE"
