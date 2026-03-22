#!/bin/bash
# SSL Certificate Setup Script
# Run after Nginx configs are in place

set -e

echo "Setting up SSL certificates with Certbot..."

# Install certbot if not present
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    apt update
    apt install -y certbot python3-certbot-nginx
fi

# Stop Nginx temporarily for standalone cert
systemctl stop nginx

# Obtain certificates
echo "Obtaining SSL certificates..."
certbot certonly --standalone \
    --preferred-challenges http-01 \
    -d logsfm.com \
    -d www.logsfm.com \
    -d radio.logsfm.com \
    --non-interactive \
    --agree-tos \
    --email admin@logsfm.com \
    --key-type rsa \
    --renew-by-default

# Restart Nginx
systemctl start nginx

echo "SSL certificates obtained successfully!"
echo "Certificate location: /etc/letsencrypt/live/logsfm.com/"
