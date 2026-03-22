# Nginx Configurations

## Archivos

- `logsfm.com` - Configuración para el sitio principal
- `radio.logsfm.com` - Configuración para el subdomain de radio
- `ssl-setup.sh` - Script para obtener certificados SSL

## Instalación

```bash
# Copiar configs
sudo cp logsfm.com /etc/nginx/sites-available/
sudo cp radio.logsfm.com /etc/nginx/sites-available/

# Habilitar sites
sudo ln -s /etc/nginx/sites-available/logsfm.com /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/radio.logsfm.com /etc/nginx/sites-enabled/

# Deshabilitar default si está activo
sudo rm /etc/nginx/sites-enabled/default 2>/dev/null || true

# Verificar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx

# Obtener certificados SSL
chmod +x ssl-setup.sh
sudo ./ssl-setup.sh

# Renew certificates (add to crontab)
# 0 0 * * * certbot renew --quiet
```

## Verificación

```bash
# Test SSL
curl -I https://logsfm.com
curl -I https://radio.logsfm.com

# Test API proxy
curl http://localhost:8001/api/status
```

## Puertos

| Servicio | Puerto |
|----------|--------|
| Nginx (HTTP) | 80 |
| Nginx (HTTPS) | 443 |
| FastAPI Backend | 8001 |
| Icecast Stream | 8000 |
| Next.js Main | 3000 |
| Next.js Radio | 3001 |
| PostgreSQL | 5432 |
