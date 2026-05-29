# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
from django.utils import timezone

from modeltranslation.admin import TabbedTranslationAdmin
from tinymce.widgets import TinyMCE

from austria_ranking.models import AustrianRanking, EmaTournamentResult, QualificationModeInfo, QuotaEvent


class QuotaEventForm(forms.ModelForm):
    class Meta:
        model = QuotaEvent
        fields = "__all__"
        widgets = {
            "event_info": TinyMCE(),
            "event_info_de": TinyMCE(),
            "event_info_en": TinyMCE(),
        }


class QualificationModeInfoForm(forms.ModelForm):
    class Meta:
        model = QualificationModeInfo
        fields = "__all__"
        widgets = {
            "info_text": TinyMCE(),
            "info_text_de": TinyMCE(),
            "info_text_en": TinyMCE(),
        }


def run_ranking_calculation(modeladmin, request, queryset):
    from austria_ranking import calculator, scraper

    for period in queryset:
        scraper.run_full_scrape(period)
        calculator.rank_players_for_period(period)
        period.calculated_at = timezone.now()
        period.save(update_fields=["calculated_at"])
    modeladmin.message_user(request, f"Ranking calculation complete for {queryset.count()} event(s).")


run_ranking_calculation.short_description = "Run ranking calculation"


@admin.register(QuotaEvent)
class QuotaEventAdmin(TabbedTranslationAdmin):
    form = QuotaEventForm
    list_display = ["name", "event_type", "start_date", "end_date", "seats_available", "calculated_at", "is_current"]
    list_filter = ["event_type", "is_current"]
    ordering = ["-end_date"]
    filter_horizontal = ["fixed_seat_players"]
    actions = [run_ranking_calculation]


@admin.register(EmaTournamentResult)
class EmaTournamentResultAdmin(admin.ModelAdmin):
    list_display = [
        "ema_id",
        "first_name",
        "last_name",
        "tournament_name",
        "tournament_country_code",
        "end_date",
        "position",
        "player_count",
        "points",
        "is_austrian_tournament",
        "quota_period",
    ]
    list_filter = ["quota_period__id", "is_austrian_tournament"]
    search_fields = ["ema_id", "first_name", "last_name", "tournament_name"]
    ordering = ["-end_date"]


@admin.register(AustrianRanking)
class AustrianRankingAdmin(admin.ModelAdmin):
    list_display = [
        "rank_position",
        "display_name",
        "ema_id",
        "at_points",
        "foreign_points",
        "total_points",
        "quota_period",
    ]
    list_filter = ["quota_period"]
    ordering = ["rank_position"]


@admin.register(QualificationModeInfo)
class QualificationModeInfoAdmin(TabbedTranslationAdmin):
    form = QualificationModeInfoForm

    def has_add_permission(self, request):
        # Only one instance allowed; hide "Add" if one already exists.
        return not QualificationModeInfo.objects.exists()
