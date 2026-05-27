# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from modeltranslation.admin import TabbedTranslationAdmin

from tournament.models import (
    MsOnlineTournamentRegistration,
    OnlineTournamentConfig,
    OnlineTournamentRegistration,
    Tournament,
    TournamentApplication,
    TournamentRegistration,
    TournamentResult,
)


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        exclude = ["registration_description", "results_description"]


class TournamentAdmin(TabbedTranslationAdmin):
    form = TournamentForm

    prepopulated_fields = {"slug": ["name"]}
    list_display = ["name", "country", "end_date", "is_upcoming", "export"]
    list_filter = ["is_event", "tournament_type", "country"]
    search_fields = ["name"]

    ordering = ["-end_date"]

    filter_horizontal = ["clubs"]

    fieldsets = [
        (None, {"fields": ["name", "slug", "country", "city", "clubs", "tournament_type", "tournament_games_type",
                           "start_date", "end_date", "number_of_sessions", "number_of_players",
                           "is_upcoming", "is_hidden", "is_event", "is_majsoul_tournament",
                           "is_pantheon_registration", "fill_city_in_registration",
                           "opened_registration", "registrations_pre_moderation",
                           "is_apply_in_rating", "is_command", "is_pre_registration", "with_confirm_code",
                           "display_notes", "share_notes", "registration_link",
                           "old_pantheon_id", "new_pantheon_id", "ema_id", "online_config"]}),
        ("Tournament Info Tab", {"fields": ["venue_address", "schedule", "lunch_options", "contact_info"]}),
        ("GDPR", {"fields": ["gdpr_document"]}),
    ]

    def export(self, obj):
        return mark_safe(
            '<a href="{}">Export to EMA</a>'.format(
                reverse("export_tournament_results", kwargs={"tournament_id": obj.id})
            )
        )


class TournamentRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "is_approved",
        "tournament",
        "first_name",
        "last_name",
        "city",
        "registration_country",
        "email",
        "phone",
        "player",
        "city_object",
        "allow_to_save_data",
    ]

    raw_id_fields = ["tournament", "player", "city_object"]
    list_filter = [["tournament", admin.RelatedOnlyFieldListFilter]]


class OnlineTournamentRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "is_approved",
        "tournament",
        "first_name",
        "last_name",
        "city",
        "registration_country",
        "tenhou_nickname",
        "contact",
        "player",
        "city_object",
        "allow_to_save_data",
    ]

    raw_id_fields = ["tournament", "player", "city_object", "user"]
    list_filter = [["tournament", admin.RelatedOnlyFieldListFilter]]


class MsOnlineTournamentRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "is_approved",
        "tournament",
        "first_name",
        "last_name",
        "city",
        "ms_friend_id",
        "ms_nickname",
        "contact",
        "player",
        "city_object",
        "allow_to_save_data",
    ]

    raw_id_fields = ["tournament", "player", "city_object", "user"]
    list_filter = [["tournament", admin.RelatedOnlyFieldListFilter]]


class TournamentApplicationAdmin(admin.ModelAdmin):
    list_display = ["tournament_name", "city", "start_date", "created_on"]


class TournamentResultAdmin(admin.ModelAdmin):
    list_display = ["tournament", "player", "place", "scores"]
    search_fields = [
        "tournament__name",
        "player__last_name",
        "player__first_name",
        "player_string",
    ]
    raw_id_fields = ["tournament", "player"]
    list_filter = [["tournament", admin.RelatedOnlyFieldListFilter]]


class OnlineTournamentConfigAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "token",
        "online_config",
    ]


admin.site.register(Tournament, TournamentAdmin)
admin.site.register(OnlineTournamentConfig, OnlineTournamentConfigAdmin)
admin.site.register(TournamentRegistration, TournamentRegistrationAdmin)
admin.site.register(OnlineTournamentRegistration, OnlineTournamentRegistrationAdmin)
admin.site.register(MsOnlineTournamentRegistration, MsOnlineTournamentRegistrationAdmin)
admin.site.register(TournamentApplication, TournamentApplicationAdmin)
admin.site.register(TournamentResult, TournamentResultAdmin)
