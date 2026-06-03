The project is working with Python **3.9+** only.

It is web-application to accumulate, calculate and display russian riichi-mahjong tournaments and ratings.

## Local

### Project set up

You need to have installed docker and docker compose.

Steps to run the project:

1. `make build-docker`
2. `make initial-data` (run this command only once, for the initial project setup)
3. `make up`

After these steps you will be able to access website here: http://0.0.0.0:8060/

## Production

### Docker set up

You need to have installed docker and docker compose.

Copy `.envs/.production.env.example` file and fill it with real data, but don't forget to keep it in secret (at least don't add it to version control system). Assign these env variables to the container with any way that is suits you (there are different options how to do it), and after that you can simply run `make build` and `make up` commands. By default in `production.yml` we are using `.envs/.production.env` file.

For static files serving and SSL configuration you need to set up the server upfront of this docker image.

If needed, restore the database backup for the new installation.

### DB Backups

On your host machine you can set up these cron commands to make backups:

```
# every 6 hours
0 */6 * * * cd /root/portal/ && make db-backup backup_type=hourly && /root/upload_files.sh
# once a week
0 0 * * 0 cd /root/portal/ && make db-backup backup_type=weekly && /root/upload_files.sh
# once a month
0 0 2 * * cd /root/portal/ && make db-backup backup_type=monthly && /root/upload_files.sh
```


### Changing translation
change translation in server/locale/django.po then run
```
docker compose exec -u root web python manage.py compilemessages
```

## Code quality

Before pushing, run the linters locally to avoid CI failures:

```bash
# Run all linters (isort + black + flake8)
make lint

# Auto-fix import order and code style
make format
```

Individual targets:

```bash
make lint-isort            # check import order (mirrors CI)
make lint-python-code-style  # check black formatting (mirrors CI)
make lint-flake8           # check flake8 (mirrors CI)
make format-isort          # fix import order
make format-python-code    # fix black formatting
```