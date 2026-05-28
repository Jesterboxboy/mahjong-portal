# Production Deployment Guide

Deploys the mahjong-portal behind nginx (reverse proxy) with TLS via Let's Encrypt.
The stack uses `deploy/docker-compose.yml` which runs gunicorn on port **6101** (internal only).

---

## Prerequisites

- A Linux server with Docker + Docker Compose installed
- nginx installed (`apt install nginx`)
- certbot installed (`apt install certbot python3-certbot-nginx`)
- A DNS A-record pointing your domain at the server IP
- Port 80 and 443 open in the firewall

---

## 1. Clone and configure

```bash
git clone https://github.com/your-org/mahjong-portal.git /srv/mahjong-portal
cd /srv/mahjong-portal/deploy
```

Create the production env file:

```bash
cp ../.envs/.local .envs/.production.env
```

Edit `.envs/.production.env` — at minimum set these values:

```env
DEBUG=false
SECRET_KEY=<long-random-string>
ALLOWED_HOSTS=yourdomain.example.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.example.com

POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=mahjong_portal
POSTGRES_USER=portal
POSTGRES_PASSWORD=<strong-password>
DATABASE_URL=postgresql://portal:<strong-password>@db:5432/mahjong_portal

PANTHEON_AUTH_API_URL=https://frey.yourdomain.example.com
PANTHEON_NEW_API_URL=https://mimir.yourdomain.example.com
PANTHEON_FRONTEND_URL=https://sigrun.yourdomain.example.com
```

> Generate a SECRET_KEY with:
> `python3 -c "import secrets; print(secrets.token_urlsafe(60))"`

---

## 2. Prepare persistent directories

The production compose mounts these bind paths under `deploy/files/`.
Create them and ensure the container user (`UID 82` for Alpine's default, or match your image) can write:

```bash
cd /srv/mahjong-portal/deploy
mkdir -p files/collected_static files/whoosh_index files/tmp files/shared files/media
```

---

## 3. Update `deploy/docker-compose.yml` for media

The upstream deploy compose does not yet include the `media_uploads` volume introduced
for django-filebrowser. Add the media mount to both `web` and `cronjobs` services:

```yaml
volumes:
  postgres_production_data: {}

services:
  web:
    ...
    volumes:
      - ./files/collected_static:/app/collected_static/
      - ./files/whoosh_index:/app/whoosh_index/
      - ./files/tmp:/tmp
      - ./files/shared/:/app/shared/
      - ./files/media:/app/media          # ← add this line
    ...

  cronjobs:
    ...
    volumes:
      - ./files/whoosh_index:/app/whoosh_index/
      - ./files/tmp:/tmp
      - ./files/media:/app/media          # ← add this line
    ...
```

---

## 4. Build / pull and start the stack

```bash
cd /srv/mahjong-portal/deploy

# Build the image locally (or pull from registry if you push to ghcr.io/…):
docker compose build

# Collect static files and run migrations:
docker compose run --rm web python manage.py collectstatic --no-input --clear
docker compose run --rm web python manage.py migrate

# Start services in the background:
docker compose up -d
```

Verify the app responds locally:

```bash
curl -s http://localhost:6101/ | head -5
```

---

## 5. Obtain a TLS certificate

Run certbot in standalone mode (nginx not yet serving the domain):

```bash
certbot certonly --standalone -d yourdomain.example.com
```

Certificates are written to `/etc/letsencrypt/live/yourdomain.example.com/`.

Certbot installs a systemd timer that auto-renews. Verify it:

```bash
systemctl status certbot.timer
```

---

## 6. nginx configuration

Create `/etc/nginx/conf.d/mahjong-portal.conf`:

```nginx
# Redirect HTTP → HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS reverse proxy
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name yourdomain.example.com;

    # TLS certificates from Let's Encrypt
    ssl_certificate     /etc/letsencrypt/live/yourdomain.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.example.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/yourdomain.example.com/chain.pem;

    # Modern TLS settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 1.1.1.1 8.8.8.8 valid=300s;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options    "nosniff" always;
    add_header X-Frame-Options           "SAMEORIGIN" always;
    add_header Referrer-Policy           "strict-origin-when-cross-origin" always;

    client_max_body_size 20M;

    # Serve Django-collected static files directly (no gunicorn round-trip)
    location /static/ {
        alias /srv/mahjong-portal/deploy/files/collected_static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Serve user-uploaded media files directly
    location /media/ {
        alias /srv/mahjong-portal/deploy/files/media/;
        expires 7d;
        add_header Cache-Control "public";
        access_log off;
    }

    # Everything else goes to gunicorn
    location / {
        proxy_pass         http://127.0.0.1:6101;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 10s;
    }
}
```

Replace `yourdomain.example.com` with your actual domain throughout.

Test and reload nginx:

```bash
nginx -t && systemctl reload nginx
```

---

## 7. Auto-renew hook

certbot's auto-renew does not reload nginx by default. Create a deploy hook:

```bash
cat > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh << 'EOF'
#!/bin/sh
systemctl reload nginx
EOF
chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
```

---

## 8. Routine updates

Use the Makefile in `deploy/`:

```bash
cd /srv/mahjong-portal/deploy
make update
```

This pulls the latest image, runs `collectstatic` + `migrate`, and restarts the stack.

---

## Summary of exposed ports

| Service  | Internal port | Exposed to host | Notes                          |
|----------|--------------|-----------------|--------------------------------|
| gunicorn | 6101         | 127.0.0.1:6101  | proxied by nginx               |
| postgres | 5432         | **not exposed** | internal Docker network only   |

> Do **not** bind postgres to a host port in production.
