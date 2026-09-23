# Restoring a mahjong-portal backup

Backups are made by `portal-backup.sh`. Each run writes one archive:

```
/mnt/backup/portal/portal-2026-09-23_033000.tar.gz
/mnt/backup/portal/latest.tar.gz -> portal-2026-09-23_033000.tar.gz
```

Each archive contains:

```
MANIFEST          # date, portal path, git commit, postgres version
portal.dump       # database, pg_dump custom format
files/media/      # user uploads
```

`latest.tar.gz` points at the newest run. On mounts without symlink support (CIFS/SMB,
FAT) the script writes `latest.txt` holding the file name instead. Unpack the newest
backup into a working directory:

```bash
PORTAL=/srv/docker-compose/mahjong-portal
ARCHIVE=/mnt/backup/portal/latest.tar.gz
[ -e "$ARCHIVE" ] || ARCHIVE=/mnt/backup/portal/$(cat /mnt/backup/portal/latest.txt)

BACKUP=$(mktemp -d)
tar xzf "$ARCHIVE" -C "$BACKUP"
cat $BACKUP/MANIFEST
```

The steps below use `$PORTAL` and that extracted `$BACKUP`. Delete it when you are done:
it holds a full copy of the database.

## 1. Restore the database into the existing instance

Use this when the data is wrong but the machine is fine. **It overwrites the current
database.** Take a fresh backup first if the current state has any value.

```bash
cd $PORTAL
docker compose stop web cron                 # stop writers, keep db running
docker compose exec -T db sh -c \
  'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists' < $BACKUP/portal.dump
docker compose start web cron
```

`--clean --if-exists` drops the existing objects before recreating them. Ignore warnings
about objects that did not exist.

Then rebuild what is derived from the database:

```bash
docker compose exec web python manage.py migrate        # no-op if code and dump match
docker compose exec web python manage.py update_index   # search index
```

## 2. Restore onto a fresh machine

1. **Install Docker and Docker Compose**, then create the external network the compose
   file expects:

   ```bash
   docker network create pantheon-connect
   ```

2. **Check out the code at the commit the backup was made from** (see `MANIFEST`):

   ```bash
   git clone <repo-url> $PORTAL && cd $PORTAL
   git checkout <commit-from-MANIFEST>
   ```

3. **Put the secrets back.** They are **not** in the backup by design — restore
   `.envs/.production.env` from your password manager. It needs at least
   `DJANGO_SECRET_KEY`, the Postgres credentials and the Pantheon settings, and the
   Postgres password must match the one the dumped database was created with.

   ```bash
   mkdir -p $PORTAL/.envs
   $EDITOR $PORTAL/.envs/.production.env
   chmod 600 $PORTAL/.envs/.production.env
   ```

4. **Start the database only**, so it initialises its volume:

   ```bash
   docker compose up -d db
   sleep 10
   ```

5. **Load the dump:**

   ```bash
   docker compose exec -T db sh -c \
     'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists' < $BACKUP/portal.dump
   ```

6. **Restore the media files:**

   ```bash
   cp -a $BACKUP/files/media/. $PORTAL/files/media/
   ```

7. **Start everything and rebuild the derived files:**

   ```bash
   docker compose up -d
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py collectstatic --no-input --clear
   docker compose exec web python manage.py update_index
   ```

## 3. Check the restore worked

```bash
cd $PORTAL
docker compose exec web python manage.py shell -c "
from tournament.models import Tournament, TournamentRegistration
print('tournaments:', Tournament.objects.count())
print('registrations:', TournamentRegistration.objects.count())
"
```

Then open the site, log in to `/admin/`, and open one tournament announcement page to
confirm media and static files are served.

The Pantheon connection is separate from the database dump: check
**Admin → Settings → Frey connector**, whose status line does a live check. If it shows
an error, log in there again with the Pantheon admin account. The connector falls back to
`PANTHEON_ADMIN_ID` / `PANTHEON_ADMIN_COOKIE` from the env file.

## What is not in the backup

- `.envs/.production.env` and any other secrets — kept in a password manager instead, so
  the backup target never holds credentials.
- `files/collected_static` — rebuilt by `collectstatic`.
- `files/whoosh_index` — rebuilt by `update_index`.
- Docker images — pulled by `docker compose up`, so pin or rebuild them from the checked-out code.

## Restoring a single table

`pg_restore` can pick one table out of the dump, which is safer than a full restore when
only one thing went wrong:

```bash
docker compose exec -T db sh -c \
  'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --data-only --table=tournament_tournamentregistration' \
  < $BACKUP/portal.dump
```

Existing rows are kept, so this appends. Delete the rows you want replaced first, or
restore into a scratch database and copy across.
