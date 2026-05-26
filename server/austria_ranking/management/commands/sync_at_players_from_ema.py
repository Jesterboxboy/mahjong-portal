# -*- coding: utf-8 -*-
"""
Management command: sync_at_players_from_ema

Scrapes the EMA Austrian RCR player list from
http://mahjong-europe.org/ranking/Country/AUT_RCR.html
and creates Player records for any EMA ID not yet in the portal.

Usage:
    python manage.py sync_at_players_from_ema
    python manage.py sync_at_players_from_ema --dry-run
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from austria_ranking.scraper import scrape_at_players
from player.models import Player
from settings.models import Country


def _unique_slug(last_name: str, first_name: str) -> str:
    """Return a slug for 'lastname firstname' that does not collide with existing Player slugs."""
    base = slugify(f"{last_name} {first_name}")
    slug = base
    counter = 2
    while Player.objects.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


class Command(BaseCommand):
    help = "Import Austrian EMA riichi players from mahjong-europe.org into the portal Player table."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print actions without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be written."))

        try:
            austria = Country.objects.get(code="AT")
        except Country.DoesNotExist:
            raise CommandError(
                "Country with code 'AT' not found in the database. "
                "Create it in Django admin (Settings → Countries) first."
            )

        self.stdout.write("Fetching Austrian player list from EMA website…")
        players = scrape_at_players()

        if not players:
            self.stdout.write(self.style.ERROR("No players returned from EMA scraper. Aborting."))
            return

        self.stdout.write(f"Found {len(players)} Austrian EMA players.")

        created = 0
        skipped = 0

        for entry in players:
            ema_id = entry["ema_id"]
            first_name = entry["first_name"]
            last_name = entry["last_name"]

            if Player.objects.filter(ema_id=ema_id).exists():
                self.stdout.write(f"  SKIP  {last_name} {first_name} (EMA {ema_id}) — already in portal")
                skipped += 1
                continue

            slug = _unique_slug(last_name, first_name)
            if dry_run:
                self.stdout.write(
                    f"  WOULD CREATE  {last_name} {first_name} (EMA {ema_id}, slug={slug})"
                )
            else:
                Player.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    slug=slug,
                    ema_id=ema_id,
                    country=austria,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"  CREATED  {last_name} {first_name} (EMA {ema_id})")
                )
            created += 1

        action = "Would create" if dry_run else "Created"
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {action} {created} player(s), skipped {skipped} existing."
            )
        )
