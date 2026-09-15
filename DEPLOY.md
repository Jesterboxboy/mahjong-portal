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
git clone https://github.com/your-org/mahjong-portal.git /srv/docker-compose/mahjong-portal
cd /srv/docker-compose/mahjong-portal/deploy
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

# Admin account used to add approved registrants to Pantheon events (see section 9)
PANTHEON_ADMIN_ID=<pantheon-person-id>
PANTHEON_ADMIN_COOKIE=<pantheon-auth-token>

# Outgoing mail (see section 8)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_HOST_USER=portal@yourdomain.example.com
EMAIL_HOST_PASSWORD=<smtp-password>
DEFAULT_FROM_EMAIL=portal@yourdomain.example.com
```

> After changing `.envs/.production.env` on a running stack, recreate the containers —
> `restart` does not reload env files:
> `docker compose up -d --force-recreate web cronjobs`

> Generate a SECRET_KEY with:
> `python3 -c "import secrets; print(secrets.token_urlsafe(60))"`

---

## 2. Prepare persistent directories

The production compose mounts these bind paths under `deploy/files/`.
Create them and ensure the container user (`UID 82` for Alpine's default, or match your image) can write:
find dockergroup and edit in Dockerfile

RUN addgroup -g 989 -S docker && adduser -u 100 -S docker-user -G docker

```bash
cd /srv/docker-compose/mahjong-portal/deploy
mkdir -p files/collected_static files/whoosh_index files/tmp files/shared files/media
sudo chgrp -R docker ./files/
sudo chmod -R g+rwX ./files/
```

docker compose build --no-cache web
docker compose run --rm web id
# uid=100(docker-user) gid=989(docker) groups=989(docker)
docker compose run --rm web python manage.py collectstatic --no-input --clear

---

## 3. Build / pull and start the stack

```bash
cd /srv/docker-compose/mahjong-portal/deploy

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

## 4. Obtain a TLS certificate

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

## 5. nginx configuration

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
        alias /srv/docker-compose/mahjong-portal/deploy/files/collected_static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Serve user-uploaded media files directly
    location /media/ {
        alias /srv/docker-compose/mahjong-portal/deploy/files/media/;
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

## 6. Auto-renew hook

certbot's auto-renew does not reload nginx by default. Reload nginx

```bash
systemctl reload nginx
```

---

## 7. Routine updates

Use the Makefile in `deploy/`:

```bash
cd /srv/docker-compose/mahjong-portal/deploy
make update
```

This pulls the latest image, runs `collectstatic` + `migrate`, and restarts the stack.

---

## 8. Email

The portal sends mail for registration confirmations, organizer notices and Pantheon sync failures.
All mail goes through SMTP using the `EMAIL_*` variables from section 1.

| Variable | Notes |
|----------|-------|
| `EMAIL_HOST` | Required. If unset, Django tries `localhost` and every send fails |
| `EMAIL_PORT` | Default `587` |
| `EMAIL_USE_TLS` / `EMAIL_USE_SSL` | `587` → TLS=true, SSL=false · `465` → TLS=false, SSL=true. Never both true |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP login |
| `DEFAULT_FROM_EMAIL` | Sender address; defaults to `EMAIL_HOST_USER`. Must be allowed by your provider |

Test it:

```bash
docker compose exec web python manage.py sendtestemail you@example.com
```

Every send attempt is recorded in **Admin → Sent emails** (`/admin/mahjong_portal/sentemail/`),
with `success` and the SMTP `error` if one occurred.

### Troubleshooting: a registrant got no confirmation email

1. **Admin → Sent emails** — is there a row for the recipient?
   - `success = False` → SMTP problem; read the `error` column, check the `EMAIL_*` values.
   - `success = True` → the SMTP server accepted it; check spam and your provider's logs.
   - **No row** → the send was skipped before SMTP. Continue with step 2.
2. Inspect the registration (replace `<ID>`):

   ```bash
   docker compose exec web python manage.py shell -c "
   from tournament.models import TournamentRegistration as R, TournamentEmailTemplate as T
   r = R.objects.get(pk=<ID>)
   print('approved:', r.is_approved)
   print('recipient used:', r.get_recipient_email())
   print('confirmation template:', r.tournament.email_templates.filter(email_type=T.CONFIRMATION).exists())
   "
   ```

   - `confirmation template: False` → add a *Confirmation* email template to the tournament in the admin.
   - `recipient used: None` → no email could be determined for the registrant.
   - The email is sent only when a registration **becomes** approved (created approved, or switched
     from unapproved to approved). Re-saving an already approved row sends nothing — untick, save,
     tick, save to re-trigger.
3. Application log:

   ```bash
   docker compose logs web --since 1h | grep -i "Failed to send notification\|smtp"
   ```

---

## 9. Pantheon admin credentials

When a registration for an offline tournament with *Is pantheon registration* is approved, the portal
adds the player to the linked Pantheon event. It authenticates as a Pantheon admin using:

| Variable | Sent as header | What it is |
|----------|----------------|------------|
| `PANTHEON_ADMIN_ID` | `X-Current-Person-Id` | Pantheon person id of the admin account |
| `PANTHEON_ADMIN_COOKIE` | `X-Auth-Token` | Auth token of that account |

The account must be allowed to add players to the event (event admin or Pantheon superadmin).

### Obtaining the values

Log in through the portal's own Pantheon client — no browser cookie extraction needed:

```bash
cd /srv/docker-compose/mahjong-portal
docker compose exec -it web python manage.py shell -c "
from getpass import getpass
from pantheon_api.api_calls.user import login_through_pantheon, get_current_pantheon_user_data
r = login_through_pantheon(input('Pantheon email: '), getpass('Password: '))
print('PANTHEON_ADMIN_ID=%s' % r.person_id)
print('PANTHEON_ADMIN_COOKIE=%s' % r.auth_token)
print('check:', get_current_pantheon_user_data(r.person_id, r.auth_token)['title'])
"
```

The `check:` line should print the account's name. Copy both values into `.envs/.production.env`, then:

```bash
docker compose up -d --force-recreate web cronjobs
docker compose exec web sh -c 'echo $PANTHEON_ADMIN_ID; echo ${PANTHEON_ADMIN_COOKIE:+token set}'
```

> The token grants full access as that account — keep it out of git, chat and screenshots.
> If pushes start failing with an auth error (e.g. after a password change), repeat the steps above.

### When a push fails

The portal registration is always kept. The error is stored on the registration
(`pantheon_sync_error`) and organizers + superusers are emailed. After fixing the cause, select the
affected rows in **Admin → Tournament registrations** and run **Retry Pantheon event registration**.

---

## Summary of exposed ports

| Service  | Internal port | Exposed to host | Notes                          |
|----------|--------------|-----------------|--------------------------------|
| gunicorn | 6101         | 127.0.0.1:6101  | proxied by nginx               |
| postgres | 5432         | **not exposed** | internal Docker network only   |

> Do **not** bind postgres to a host port in production.



## migrations

docker compose run --rm --user root web sh -c "python manage.py makemigrations && python manage.py migrate"