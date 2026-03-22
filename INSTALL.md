# Radio Platform - Installation Guide

## Quick Start (Development with Docker)

```bash
# Clone or navigate to the project directory
cd C:\Users\Usuario\Desktop\radio-dev

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

## Services

| Service | Port | URL |
|---------|------|-----|
| Frontend (logsfm.com) | 3000 | http://localhost:3000 |
| Radio Subdomain | 3001 | http://localhost:3001 |
| Backend API | 8001 | http://localhost:8001 |
| Icecast Stream | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | localhost:5432 |

## Manual Installation (Server)

### 1. Install Dependencies

```bash
# Ubuntu/Debian
apt update && apt upgrade -y
apt install -y git curl wget

# Install Docker
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install PostgreSQL
apt install -y postgresql postgresql-contrib

# Install Nginx
apt install -y nginx certbot python3-certbot-nginx
```

### 2. Clone Project

```bash
cd /var/www
git clone <repository-url> radio-platform
cd radio-platform
```

### 3. Database Setup

```bash
# Start PostgreSQL
systemctl enable postgresql
systemctl start postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE radio_db;"
sudo -u postgres psql -c "CREATE USER radio WITH PASSWORD 'RadioPass123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE radio_db TO radio;"

# Create tables
sudo -u postgres psql -d radio_db -f backend/schema.sql
```

### 4. Configure Backend

```bash
cd /var/www/radio-platform/backend
cp .env.example .env
nano .env  # Edit with your values
pip install -r requirements.txt
```

### 5. Configure Frontend

```bash
cd /var/www/radio-platform/frontend
npm install
npm run build
```

### 6. Nginx Setup

```bash
# Copy configurations
cp nginx/logsfm.com /etc/nginx/sites-available/
cp nginx/radio.logsfm.com /etc/nginx/sites-available/

# Enable sites
ln -s /etc/nginx/sites-available/logsfm.com /etc/nginx/sites-enabled/
ln -s /etc/nginx/sites-available/radio.logsfm.com /etc/nginx/sites-enabled/

# Remove default site
rm /etc/nginx/sites-enabled/default

# Test and reload
nginx -t
systemctl reload nginx

# Get SSL certificates
certbot --nginx -d logsfm.com -d www.logsfm.com -d radio.logsfm.com
```

### 7. Start Services

```bash
# Start backend
cd /var/www/radio-platform/backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# Start Icecast
ezstream -c /var/www/radio-platform/ezstream.xml &

# Or use systemd for auto-start (see backend/README.md)
```

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Default Admin User

After first run, create admin via API:

```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@logsfm.com",
    "password": "admin123",
    "display_name": "Administrator"
  }'
```

Then manually update role to 'admin' in database:

```sql
UPDATE users SET role = 'admin' WHERE username = 'admin';
```

## Troubleshooting

### Icecast not streaming
```bash
# Check if ezstream is running
ps aux | grep ezstream

# Check Icecast logs
tail -f /var/log/icecast2/error.log

# Verify playlist exists
cat /var/lib/icecast2/playlist.txt
```

### Backend API not responding
```bash
# Check if uvicorn is running
ps aux | grep uvicorn

# Check logs
curl http://localhost:8001/api/status
```

### Database connection issues
```bash
# Test PostgreSQL connection
psql -U radio -d radio_db -h localhost

# Check connection string
# Ensure password matches in .env and DATABASE_URL
```

## Production Checklist

- [ ] Change SECRET_KEY in .env
- [ ] Update ICECAST passwords
- [ ] Configure firewall (ufw allow 80,443,8000,8001)
- [ ] Setup SSL certificates
- [ ] Configure automated backups for PostgreSQL
- [ ] Setup monitoring (Prometheus/Grafana optional)
- [ ] Configure log rotation
