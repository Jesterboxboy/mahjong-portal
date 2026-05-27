# -*- coding: utf-8 -*-
"""
Management command: calculate_austrian_ranking

Runs the full scrape + ranking calculation for every QuotaEvent that has
is_current=True.  Mirrors what the admin "Run Calculation" button does.

Usage:
    python manage.py calculate_austrian_ranking
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from austria_ranking import calculator, scraper
from austria_ranking.models import QuotaEvent


class Command(BaseCommand):
    help = "Scrape EMA results and recalculate AustrianRanking for all current QuotaEvents."

    def handle(self, *args, **options):
        periods = list(QuotaEvent.objects.filter(is_current=True))

        if not periods:
            self.stdout.write(self.style.WARNING("No current QuotaEvents found — nothing to do."))
            return

        self.stdout.write(f"Found {len(periods)} current quota event(s).")

        for period in periods:
            self.stdout.write(f"\nProcessing: {period} …")
            try:
                created, skipped = scraper.run_full_scrape(period)
                self.stdout.write(f"  Scraped: {created} new results, {skipped} already present.")
                calculator.rank_players_for_period(period)
                period.calculated_at = timezone.now()
                period.save(update_fields=["calculated_at"])
                self.stdout.write(self.style.SUCCESS(f"  Done: {period}"))
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"  Error processing {period}: {exc}"))
