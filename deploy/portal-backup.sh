#!/bin/bash
# Backup a running mahjong-portal instance: database and media, one tar.gz per run.
# Secrets (.envs/*.env) are deliberately NOT included - keep them in a password manager.
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

die() { echo "portal-backup: $*" >&2; exit 1; }

[[ -d "$PORTAL_DIR" ]] || die "portal dir not found: $PORTAL_DIR"
cd "$PORTAL_DIR"
[[ -f docker-compose.yml ]] || die "no docker-compose.yml in $PORTAL_DIR"

# A missing backup mount would otherwise silently fill the root filesystem.
mountpoint -q "$(dirname "$BACKUP_DIR")" || [[ -d "$BACKUP_DIR" ]] ||
    die "backup target not available: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Never let two runs (or a run and a slow predecessor) overlap. The lock lives on local
# disk: network mounts do not reliably support flock.
exec 9>"${LOCK_FILE:-/run/portal-backup.lock}"
flock -n 9 || die "another backup is still running"

STAMP="$(date +%Y-%m-%d_%H%M%S)"
ARCHIVE="$BACKUP_DIR/portal-$STAMP.tar.gz"

# The run is assembled on local disk and only the finished archive is written to the
# backup target, so a partial file never appears there.
WORK="$(mktemp -d "${TMPDIR:-/var/tmp}/portal-backup.XXXXXX")"
trap 'rm -rf "$WORK"; rm -f "$ARCHIVE.part"' EXIT

if ! docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB"' > "$WORK/portal.dump"; then
    die "pg_dump failed - is the db container running? (docker compose ps)"
fi
[[ -s "$WORK/portal.dump" ]] || die "database dump is empty"

# Record what produced this backup, so a restore can check out the matching code.
{
    echo "date:     $(date -Is)"
    echo "portal:   $PORTAL_DIR"
    echo "git:      $(git -C "$PORTAL_DIR" rev-parse HEAD 2>/dev/null || echo unknown)"
    echo "postgres: $(docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "select version()"' || true)"
} > "$WORK/MANIFEST"

# Media is user-uploaded and not reproducible; static files and the search index are, so
# they are skipped. Media goes in uncompressed - the outer gzip handles it.
media_args=()
[[ -d files/media ]] && media_args=(-C "$PORTAL_DIR" files/media)

tar czf "$ARCHIVE.part" -C "$WORK" portal.dump MANIFEST "${media_args[@]}"
# Catches a truncated write, which is the failure a backup must never hide.
tar tzf "$ARCHIVE.part" > /dev/null || die "archive is corrupt: $ARCHIVE.part"
mv "$ARCHIVE.part" "$ARCHIVE"

# Pointer to the newest run. CIFS/SMB and FAT mounts have no symlinks, so fall back to a
# text file; RESTORE.md reads both.
if ! ln -sfn "$ARCHIVE" "$BACKUP_DIR/latest.tar.gz" 2>/dev/null; then
    rm -f "$BACKUP_DIR/latest.tar.gz"
    basename "$ARCHIVE" > "$BACKUP_DIR/latest.txt"
fi

# Rotation: keep the newest $KEEP archives.
find "$BACKUP_DIR" -mindepth 1 -maxdepth 1 -type f -name 'portal-20*.tar.gz' -printf '%f\n' |
    sort -r | tail -n "+$((KEEP + 1))" |
    while read -r old; do rm -f "$BACKUP_DIR/$old"; done

echo "portal-backup: ok $ARCHIVE ($(du -sh "$ARCHIVE" | cut -f1))"
