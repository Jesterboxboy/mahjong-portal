# -*- coding: utf-8 -*-

import logging
from datetime import timezone as dt_timezone

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from austria_ranking.models import QuotaPeriod

logger = logging.getLogger(__name__)


@staff_member_required
def run_ranking_calculation(request, pk: int):
    period = get_object_or_404(QuotaPeriod, pk=pk)

    if request.method == "POST":
        from austria_ranking import calculator, scraper

        try:
            created, skipped = scraper.run_full_scrape(period)
            calculator.rank_players_for_period(period)
            period.calculated_at = timezone.now()
            period.save(update_fields=["calculated_at"])
            logger.info(
                "Ranking calculation for %s complete: %d new results, %d skipped",
                period,
                created,
                skipped,
            )
            from django.contrib import messages

            messages.success(
                request,
                f"Calculation for '{period}' complete: {created} new results scraped, {skipped} already present.",
            )
        except Exception as exc:
            logger.exception("Error during ranking calculation for %s", period)
            from django.contrib import messages

            messages.error(request, f"Error during calculation: {exc}")

        return redirect("admin:austria_ranking_quotaperiod_changelist")

    return render(request, "austria_ranking/confirm_run.html", {"period": period})
