# -*- coding: utf-8 -*-

import csv

from django.core.management.base import BaseCommand

from player.models import Player


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("export_players.csv", "w") as f:
            writer = csv.writer(f)

            players = Player.objects.all()

            rows = [["id", "last_name", "first_name", "ema_id"]]

            for player in players:
                rows.append(
                    [
                        player.id,
                        player.last_name,
                        player.first_name,
                        player.ema_id,
                    ]
                )

            for x in rows:
                writer.writerow(x)
