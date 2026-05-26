# -*- coding: utf-8 -*-
"""
Management command: enrich_players_from_pantheon

For Austrian Player records that have no pantheon_id set, attempts to find a
matching Pantheon (Frey) person by searching for "Firstname Lastname" via the
FindByTitle API. On a single unambiguous match, stores the Frey person_id in
Player.pantheon_id.

Requires settings.PANTHEON_AUTH_API_URL to be configured.

Usage:
    python manage.py enrich_players_from_pantheon
    python manage.py enrich_players_from_pantheon --dry-run
    python manage.py enrich_players_from_pantheon --all   # re-check players that already have pantheon_id
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from twirp.context import Context
from twirp.exceptions import TwirpServerException

from pantheon_api import frey_pb2
from pantheon_api.frey_twirp import FreyClient
from player.models import Player


class Command(BaseCommand):
    help = (
        "Match Austrian Player records against Pantheon (Frey) by name and store "
        "the Frey person_id in Player.pantheon_id."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print match results without writing to the database.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            default=False,
            help="Also re-check players that already have a pantheon_id set.",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        check_all: bool = options["all"]

        if not getattr(settings, "PANTHEON_AUTH_API_URL", None):
            raise CommandError(
                "settings.PANTHEON_AUTH_API_URL is not configured. "
                "Set the PANTHEON_AUTH_API_URL environment variable and retry."
            )

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be written."))

        client = FreyClient(settings.PANTHEON_AUTH_API_URL)

        qs = Player.objects.filter(country__code="AT")
        if not check_all:
            qs = qs.filter(pantheon_id__isnull=True)

        players = list(qs.order_by("last_name", "first_name"))
        self.stdout.write(f"Checking {len(players)} Austrian player(s) against Pantheon…\n")

        matched = 0
        skipped_ambiguous = 0
        skipped_no_match = 0
        already_set = 0

        for player in players:
            query = f"{player.first_name} {player.last_name}"

            try:
                response = client.FindByTitle(
                    ctx=Context(),
                    request=frey_pb2.PersonsFindByTitlePayload(query=query),
                    server_path_prefix="/v2",
                    timeout=15,
                )
                candidates = list(response.people)
            except TwirpServerException as exc:
                self.stdout.write(
                    self.style.ERROR(f"  ERROR  {player} (EMA {player.ema_id}): Frey API error — {exc}")
                )
                continue

            if len(candidates) == 0:
                self.stdout.write(
                    f"  NO MATCH  {player} (EMA {player.ema_id}) — query: '{query}'"
                )
                skipped_no_match += 1

            elif len(candidates) == 1:
                person = candidates[0]

                if player.pantheon_id == person.id:
                    self.stdout.write(
                        f"  ALREADY SET  {player} (EMA {player.ema_id}) → Pantheon #{person.id} '{person.title}'"
                    )
                    already_set += 1
                    continue

                if dry_run:
                    self.stdout.write(
                        f"  WOULD LINK  {player} (EMA {player.ema_id}) → Pantheon #{person.id} '{person.title}'"
                    )
                else:
                    player.pantheon_id = person.id
                    player.save(update_fields=["pantheon_id"])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  LINKED  {player} (EMA {player.ema_id}) → Pantheon #{person.id} '{person.title}'"
                        )
                    )
                matched += 1

            else:
                names = ", ".join(f"#{p.id} '{p.title}'" for p in candidates)
                self.stdout.write(
                    self.style.WARNING(
                        f"  AMBIGUOUS  {player} (EMA {player.ema_id}) — {len(candidates)} candidates: {names}"
                    )
                )
                skipped_ambiguous += 1

        action = "Would link" if dry_run else "Linked"
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {action} {matched}, "
                f"no match {skipped_no_match}, "
                f"ambiguous {skipped_ambiguous}, "
                f"already set {already_set}."
            )
        )
