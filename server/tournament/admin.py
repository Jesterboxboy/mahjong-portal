# -*- coding: utf-8 -*-

import re
from datetime import date, datetime

from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from modeltranslation.admin import TabbedTranslationAdmin
from tinymce.widgets import TinyMCE

from settings.models import Country
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
        widgets = {
            "venue_address": TinyMCE(),
            "venue_address_de": TinyMCE(),
            "venue_address_en": TinyMCE(),
            "schedule": TinyMCE(),
            "schedule_de": TinyMCE(),
            "schedule_en": TinyMCE(),
            "lunch_options": TinyMCE(),
            "lunch_options_de": TinyMCE(),
            "lunch_options_en": TinyMCE(),
            "contact_info": TinyMCE(),
            "contact_info_de": TinyMCE(),
            "contact_info_en": TinyMCE(),
        }


class TournamentAdmin(TabbedTranslationAdmin):
    form = TournamentForm

    prepopulated_fields = {"slug": ["name"]}
    list_display = ["name", "country", "end_date", "is_upcoming", "export"]
    list_filter = ["is_event", "tournament_type", "country"]
    search_fields = ["name"]

    ordering = ["-end_date"]

    filter_horizontal = ["clubs"]

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "name",
                    "slug",
                    "country",
                    "city",
                    "clubs",
                    "tournament_type",
                    "tournament_games_type",
                    "start_date",
                    "end_date",
                    "number_of_sessions",
                    "number_of_players",
                    "is_upcoming",
                    "is_hidden",
                    "is_event",
                    "is_majsoul_tournament",
                    "is_pantheon_registration",
                    "fill_city_in_registration",
                    "opened_registration",
                    "registrations_pre_moderation",
                    "is_apply_in_rating",
                    "is_command",
                    "is_pre_registration",
                    "with_confirm_code",
                    "display_notes",
                    "share_notes",
                    "registration_link",
                    "old_pantheon_id",
                    "new_pantheon_id",
                    "ema_id",
                    "online_config",
                ]
            },
        ),
        ("Tournament Info Tab", {"fields": ["venue_address", "schedule", "lunch_options", "contact_info"]}),
        ("GDPR", {"fields": ["gdpr_document", "gdpr_file"]}),
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


def _parse_date(value):
    """Try to parse a date string, returning None on failure."""
    if not value:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None


def create_tournament_from_application(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(
            request,
            "Please select exactly one application to create a tournament from.",
            level=messages.WARNING,
        )
        return

    app = queryset.first()

    # Resolve country
    country_obj = None
    if app.country:
        country_obj = Country.objects.filter(name__iexact=app.country.strip()).first()
        if country_obj is None:
            country_obj = Country.objects.filter(code__iexact=app.country.strip()).first()
    if country_obj is None:
        country_obj = Country.objects.first()

    # Parse dates
    end_date = _parse_date(app.end_date) or _parse_date(app.start_date) or date.today()
    start_date = _parse_date(app.start_date)

    # Build unique slug
    base_slug = slugify(app.tournament_name)[:240]
    slug = base_slug
    counter = 1
    while Tournament.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # tournament_type matches now
    t_type = app.tournament_type if app.tournament_type in ("ema", "other", "online") else "other"
    t_games_type = Tournament.ONLINE_GAMES if t_type == "online" else Tournament.OFFLINE_GAMES

    # Build contact info for DE from organizer fields
    contact_parts_de = []
    if app.organizer_name:
        contact_parts_de.append(app.organizer_name)
    if app.organizer_email:
        contact_parts_de.append(app.organizer_email)
    if app.organizer_phone:
        contact_parts_de.append(app.organizer_phone)
    derived_contact_de = "\n".join(contact_parts_de) if contact_parts_de else None

    tournament = Tournament(
        name=app.tournament_name,
        slug=slug,
        country=country_obj,
        tournament_type=t_type,
        tournament_games_type=t_games_type,
        end_date=end_date,
        start_date=start_date,
        is_upcoming=True,
        # Venue: use detailed field if set, fall back to legacy address
        venue_address_de=app.venue_address_de or app.address or None,
        venue_address_en=app.venue_address_en or None,
        schedule_de=app.schedule_de or None,
        schedule_en=app.schedule_en or None,
        lunch_options_de=app.lunch_options_de or None,
        lunch_options_en=app.lunch_options_en or None,
        contact_info_de=app.contact_info_de or derived_contact_de,
        contact_info_en=app.contact_info_en or None,
        number_of_sessions=app.number_of_games or 0,
    )
    tournament.save()

    modeladmin.message_user(
        request,
        f'Tournament "{tournament.name}" created. Please review and complete the details.',
        level=messages.SUCCESS,
    )
    return HttpResponseRedirect(reverse("admin:tournament_tournament_change", args=[tournament.pk]))


create_tournament_from_application.short_description = "Create Tournament from application"


class TournamentApplicationAdmin(admin.ModelAdmin):
    list_display = ["tournament_name", "city", "start_date", "created_on"]
    actions = [create_tournament_from_application]


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
