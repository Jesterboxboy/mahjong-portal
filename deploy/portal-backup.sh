#!/bin/bash
# Backup a running mahjong-portal instance: database, media, env file.
# Safe to run while the portal is up (pg_dump is consistent, media is copied read-only).
#
# Usage:  portal-backup.sh [PORTAL_DIR] [BACKUP_DIR]
# Cron:   30 3 * * * /root/portal-backup.sh >> /var/log/portal-backup.log 2>&1
#
# Restore instructions: RESTORE.md next to this script.

set -euo pipefail

PORTAL_DIR="${1:-/srv/docker-compose/mahjong-portal}"
BACKUP_DIR="${2:-/mnt/backup/portal}"
KEEP="${KEEP:-14}"              # number of runs to keep
ENV_FILE="${ENV_FILE:-.envs/.production.env}"

die() { echo "portal-backup: $*" >&2; exit 1; }

[[ -d "$PORTAL_DIR" ]] || die "portal dir not found: $PORTAL_DIR"
cd "$PORTAL_DIR"
[[ -f "$ENV_FILE" ]] || die "env file not found: $PORTAL_DIR/$ENV_FILE"

# A missing backup mount would otherwise silently fill the root filesystem.
mountpoint -q "$(dirname "$BACKUP_DIR")" || [[ -d "$BACKUP_DIR" ]] ||
    die "backup target not available: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Never let two runs (or a run and a slow predecessor) overlap.
exec 9>"$BACKUP_DIR/.lock"
flock -n 9 || die "another backup is still running"

STAMP="$(date +%Y-%m-%d_%H%M%S)"
TARGET="$BACKUP_DIR/$STAMP"
mkdir -p "$TARGET"
# A failed run must not leave a half-written directory behind to be mistaken for a backup.
trap 'rm -rf "$TARGET"' ERR

if ! docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB"' > "$TARGET/portal.dump"; then
    rm -rf "$TARGET"
    die "pg_dump failed - is the db container running? (docker compose ps)"
fi
[[ -s "$TARGET/portal.dump" ]] || die "database dump is empty"

# Media is user-uploaded and not reproducible; static files and the search index are, so they are skipped.
if [[ -d files/media ]]; then
    tar czf "$TARGET/media.tar.gz" files/media
fi

# Contains the Pantheon token and DB password: keep it unreadable for anybody but root.
cp "$ENV_FILE" "$TARGET/production.env"
chmod 600 "$TARGET/production.env"

# Record what produced this backup, so a restore can check out the matching code.
{
    echo "date:     $(date -Is)"
    echo "portal:   $PORTAL_DIR"
    echo "git:      $(git -C "$PORTAL_DIR" rev-parse HEAD 2>/dev/null || echo unknown)"
    echo "postgres: $(docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "select version()"' || true)"
} > "$TARGET/MANIFEST"

trap - ERR
ln -sfn "$TARGET" "$BACKUP_DIR/latest"

# Rotation: keep the newest $KEEP timestamped dirs.
find "$BACKUP_DIR" -mindepth 1 -maxdepth 1 -type d -name '20*' -printf '%f\n' |
    sort -r | tail -n "+$((KEEP + 1))" |
    while read -r old; do rm -rf "$BACKUP_DIR/$old"; done

echo "portal-backup: ok $TARGET ($(du -sh "$TARGET" | cut -f1))"
