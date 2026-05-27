# -*- coding: utf-8 -*-

import logging

from django.utils import timezone

from player.models import Player
from rating.models import RatingResult

logger = logging.getLogger(__name__)


class RatingEMACalculation:
    """
    EMA rating calculation sourced directly from the EMA ranking website.

    Instead of computing scores from local tournament results, this class
    scrapes http://mahjong-europe.org/ranking/Country/AUT_RCR.html and
    stores the official EMA total points and global rank for each Austrian
    player that has a matching Player record in the portal.
    """

    USE_SCRAPER = True

    def get_date(self, rating_date):
        return rating_date

    def calculate_players_rating_rank(self, rating, rating_date):
        from austria_ranking.scraper import scrape_at_ranking

        entries = scrape_at_ranking()
        if not entries:
            logger.warning("EMA scraper returned no entries — skipping RatingResult creation.")
            return

        # entries are already sorted by total_points descending
        results = []
        place = 1
        for entry in entries:
            try:
                player = Player.objects.get(ema_id=entry["ema_id"])
            except Player.DoesNotExist:
                logger.debug(
                    "No portal player found for EMA ID %s (%s %s)",
                    entry["ema_id"],
                    entry["first_name"],
                    entry["last_name"],
                )
                continue

            results.append(
                RatingResult(
                    rating=rating,
                    player=player,
                    score=entry["total_points"],
                    place=place,
                    date=rating_date,
                    tournament_numbers=None,
                    rating_calculation=f"EMA Global Rank: {entry['ema_rank']}",
                )
            )
            place += 1

        RatingResult.objects.bulk_create(results)
        rating.updated_on = timezone.now()
        rating.save()
        logger.info("EMA rating: saved %d results for %s", len(results), rating_date)
