# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from player.models import Player
from tournament.models import Tournament, TournamentResult
from utils.new_pantheon import get_rating_table


class Command(BaseCommand):
    help = "Import tournament results from a Pantheon event into the portal."

    def add_arguments(self, parser):
        parser.add_argument(
            "tournament_slug",
            type=str,
            help="Slug of the portal Tournament to import results into.",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            default=False,
            help="Delete existing results before importing.",
        )

    def handle(self, *args, **options):
        slug = options["tournament_slug"]
        overwrite = options["overwrite"]

        try:
            tournament = Tournament.objects.get(slug=slug)
        except Tournament.DoesNotExist as exc:
            raise CommandError(f"Tournament with slug {slug!r} not found.") from exc

        if not tournament.new_pantheon_id:
            raise CommandError(f"Tournament {slug!r} has no new_pantheon_id set.")

        self.stdout.write(f"Fetching results for Pantheon event {tournament.new_pantheon_id}...")
        response = get_rating_table(tournament.new_pantheon_id)
        players_in_rating = response.list

        if not players_in_rating:
            raise CommandError("Pantheon returned an empty rating table.")

        self.stdout.write(f"Got {len(players_in_rating)} players from Pantheon.")

        with transaction.atomic():
            if overwrite:
                deleted, _ = TournamentResult.objects.filter(tournament=tournament).delete()
                self.stdout.write(f"Deleted {deleted} existing results.")

            for place, entry in enumerate(players_in_rating, start=1):
                pantheon_id = entry.id
                title = entry.title
                scores = round(entry.rating, 2)

                player = None
                try:
                    player = Player.objects.get(pantheon_id=pantheon_id)
                except Player.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Place {place}: no portal player found for Pantheon ID {pantheon_id} ({title}) — "
                            f"saving as player_string."
                        )
                    )

                TournamentResult.objects.create(
                    tournament=tournament,
                    player=player,
                    player_string=title if player is None else "",
                    place=place,
                    scores=scores,
                    games=entry.games_played,
                )
                self.stdout.write(f"  Place {place}: {title} (scores={scores})")

        self.stdout.write(self.style.SUCCESS(f"Done. Imported {len(players_in_rating)} results."))
