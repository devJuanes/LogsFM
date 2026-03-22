# Radio - Guía de Instalación para Servidor KVM (Hostiger)

## Requisitos del Servidor

- Ubuntu 20.04/22.04 LTS (recomendado)
- 1 GB RAM mínimo
- 20 GB disco
- Acceso SSH root o sudo

---

## 1. Actualizar Sistema

```bash
apt update && apt upgrade -y
```

---

## 2. Instalar Icecast2 (Servidor de Streaming)

```bash
apt install -y icecast2
```

### Configurar Icecast2

Editar `/etc/icecast2/icecast.xml`:

```bash
nano /etc/icecast2/icecast.xml
```

Cambiar passwords en `<authentication>`:
```xml
<source-password>tu_password_fuerte</source-password>
<admin-password>tu_password_admin</admin-password>
<relay-password>tu_password_relay</relay-password>
```

Habilitar Icecast:
```bash
nano /etc/default/icecast2
# Cambiar: ENABLE=true
```

Iniciar Icecast:
```bash
systemctl enable icecast2
systemctl start icecast2
```

Verificar: `http://TU_IP:8000`

---

## 3. Instalar Ezstream (Streamer)

```bash
apt install -y ezstream
```

### Crear archivo de configuración Ezstream

```bash
nano /etc/icecast2/ezstream.xml
```

Contenido:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ezstream>
    <url>http://localhost:8000/stream</url>
    <sourcepassword>tu_password_fuerte</sourcepassword>
    <filename>/var/lib/icecast2/playlist.txt</filename>
    <format>MP3</format>
    <stream_once>0</stream_once>
    <reconnect>1</reconnect>
    <reconnect_waitsec>5</reconnect_waitsec>
    <shuffle>1</shuffle>
    <svrinfoname>Mi Radio</svrinfoname>
    <svrinfourl>http://tu-dominio.com</svrinfourl>
    <svrinfogenre>radio</svrinfogenre>
    <svrinfodescription>Radio en vivo</svrinfodescription>
    <svrinfobitrate>128</svrinfobitrate>
    <svrinfochannels>2</svrinfochannels>
    <svrinfosamplerate>44100</svrinfosamplerate>
</ezstream>
```

---

## 4. Crear Directorios

```bash
mkdir -p /var/lib/icecast2/media
chown -R icecast:icecast /var/lib/icecast2/media
chmod -R 755 /var/lib/icecast2/media
```

---

## 5. Subir Archivos MP3

Usa SCP o SFTP para subir tus archivos MP3:

```bash
scp "C:\Users\Usuario\Music\JuanOnBeat.mp3" root@http://187.124.144.29:/var/lib/icecast2/media/
scp miCapsula01.mp3 root@TU_SERVIDOR:/var/lib/icecast2/media/
```

---

## 6. Crear Playlist

```bash
# Ir al directorio media
cd /var/lib/icecast2/media

# Crear playlist con todos los MP3
find . -name "*.mp3" | sort > /var/lib/icecast2/playlist.txt

# Ver playlist
cat /var/lib/icecast2/playlist.txt
```

---

## 7. Instalar y Ejecutar Backend (Opcional - API REST)

```bash
# Instalar Python y dependencias
apt install -y python3 python3-pip python3-venv

# Crear usuario para la app
useradd -m -s /bin/bash radio
su - radio

# Crear entorno virtual
python3 -m venv radioenv
source radioenv/bin/activate

# Copiar backend (desde tu proyecto)
mkdir -p ~/radio-backend
# Copia los archivos del backend a ~/radio-backend/

# Instalar dependencias
cd ~/radio-backend
    pip install -r requirements.txt

# Crear archivo de configuración
nano config.json
# { "media_dir": "/var/lib/icecast2/media/", "playlist_file": "/var/lib/icecast2/playlist.txt" }

# Ejecutar
python main.py
```

### Usar systemd para auto-inicio del backend

```bash
sudo nano /etc/systemd/system/radio-backend.service
```

Contenido:
```ini
[Unit]
Description=Radio Backend API
After=network.target

[Service]
User=radio
WorkingDirectory=/home/radio/radio-backend
ExecStart=/home/radio/radioenv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable radio-backend
systemctl start radio-backend
```

---

## 8. Iniciar Streaming

```bash
# Como usuario root o icecast
ezstream -c /etc/icecast2/ezstream.xml &
```

Para auto-iniciar, agregar a `/etc/rc.local`:
```bash
ezstream -c /etc/icecast2/ezstream.xml &
```

---

## 9. Firewall

```bash
ufw allow 22    # SSH
ufw allow 8000  # Icecast
ufw allow 8001  # Backend API
uff enable
```

---

## 10. Verificar que Todo Funciona

```bash
# Ver si Icecast está corriendo
curl http://localhost:8000/status.xsl

# Ver si Ezstream está transmitiendo
ps aux | grep ezstream

# Ver logs de Icecast
tail -f /var/log/icecast2/error.log
tail -f /var/log/icecast2/access.log
```

---

## URLs de Acceso

- **Icecast Admin**: `http://TU_IP:8000/admin/`
- **Stream**: `http://TU_IP:8000/stream`
- **API Backend**: `http://TU_IP:8001/`

---

## Comandos Útiles

```bash
# Reiniciar Icecast
systemctl restart icecast2

# Reiniciar Ezstream
pkill ezstream
ezstream -c /etc/icecast2/ezstream.xml &

# Actualizar playlist cuando agregues MP3
find /var/lib/icecast2/media -name "*.mp3" | sort > /var/lib/icecast2/playlist.txt

# Reiniciar backend
systemctl restart radio-backend
```

---

## Troubleshooting

### No hay sonido
- Verificar que los MP3 no estén corruptos: `file *.mp3`
- Verificar permisos: `ls -la /var/lib/icecast2/media/`

### Conexión rechazada
- Verificar que Icecast esté escuchando: `netstat -tlnp | grep 8000`
- Revisar firewall: `ufw status`

### Ezstream no conecta
- Verificar password en ezstream.xml coincida con icecast.xml
- Revisar logs: `tail /var/log/icecast2/error.log`
