# -*- coding: utf-8 -*-

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from austria_ranking.models import AustrianRanking, EmaTournamentResult, QuotaEvent


@admin.register(QuotaEvent)
class QuotaEventAdmin(admin.ModelAdmin):
    list_display = ["name", "event_type", "start_date", "end_date", "seats_available", "calculated_at", "is_current", "run_button"]
    list_filter = ["event_type", "is_current"]
    ordering = ["-end_date"]

    def run_button(self, obj):
        url = reverse("austria_ranking_run", args=[obj.pk])
        return format_html('<a class="button" href="{}">Run Calculation</a>', url)

    run_button.short_description = "Action"
    run_button.allow_tags = True


@admin.register(EmaTournamentResult)
class EmaTournamentResultAdmin(admin.ModelAdmin):
    list_display = ["ema_id", "first_name", "last_name", "tournament_name", "tournament_country_code", "end_date", "position", "player_count", "points", "is_austrian_tournament", "quota_period"]
    list_filter = ["quota_period__id", "is_austrian_tournament"]
    search_fields = ["ema_id", "first_name", "last_name", "tournament_name"]
    ordering = ["-end_date"]


@admin.register(AustrianRanking)
class AustrianRankingAdmin(admin.ModelAdmin):
    list_display = ["rank_position", "display_name", "ema_id", "at_points", "foreign_points", "total_points", "quota_period"]
    list_filter = ["quota_period"]
    ordering = ["rank_position"]
