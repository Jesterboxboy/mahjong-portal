# -*- coding: utf-8 -*-

from datetime import date, datetime

from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from modeltranslation.admin import TranslationAdmin
from tinymce.widgets import TinyMCE

from mahjong_portal.notifications import bulk_email_recipients, send_bulk_email, waitlist_email
from player.models import Player
from settings.models import Country
from tournament.models import (
    MsOnlineTournamentRegistration,
    OnlineTournamentConfig,
    OnlineTournamentRegistration,
    Tournament,
    TournamentApplication,
    TournamentEmailTemplate,
    TournamentRegistration,
    TournamentResult,
)
from utils.new_pantheon import get_rating_table


def _confirm_bulk_email(modeladmin, request, queryset, email_type, action_name, audience):
    """Show every address the send would reach, then send on the confirming POST.

    A bulk send cannot be taken back, so the recipient list is always shown first —
    built from the same bulk_email_recipients() call that the send then uses.
    """
    plan = [
        {
            "tournament": tournament,
            "template": tournament.email_templates.filter(email_type=email_type).first(),
            "recipients": bulk_email_recipients(tournament, email_type),
        }
        for tournament in queryset
    ]

    if request.POST.get("confirmed"):
        total = sum(send_bulk_email(entry["tournament"], email_type, entry["recipients"]) for entry in plan)
        modeladmin.message_user(request, f"Email sent to {total} recipient(s).", level=messages.SUCCESS)
        return None

    return render(
        request,
        "admin/tournament/confirm_bulk_email.html",
        {
            "plan": plan,
            "total": sum(len(entry["recipients"]) for entry in plan),
            "missing_template": [entry["tournament"] for entry in plan if not entry["template"]],
            "audience": audience,
            "action_name": action_name,
            "tournament_pks": list(queryset.values_list("pk", flat=True)),
        },
    )


def send_registrant_email(modeladmin, request, queryset):
    """Send each selected tournament's registrant email to all its approved players."""
    return _confirm_bulk_email(
        modeladmin,
        request,
        queryset,
        TournamentEmailTemplate.REGISTRANT,
        "send_registrant_email",
        "approved players only",
    )


send_registrant_email.short_description = "Send bulk email to approved players"


def send_email_to_all(modeladmin, request, queryset):
    """Send each selected tournament's "email to all" template to every registrant."""
    return _confirm_bulk_email(
        modeladmin,
        request,
        queryset,
        TournamentEmailTemplate.ALL,
        "send_email_to_all",
        "approved, waitlisted and unapproved registrants",
    )


send_email_to_all.short_description = "Send email to all registered players (incl. waitlist & unapproved)"


def approve_and_send_confirmation(modeladmin, request, queryset):
    """Approve the selected registrations (triggers the confirmation email on save)."""
    count = 0
    for registration in queryset.filter(is_approved=False):
        registration.is_approved = True
        registration.save()
        count += 1
    modeladmin.message_user(request, f"Approved {count} registration(s).", level=messages.SUCCESS)


approve_and_send_confirmation.short_description = "Approve & send confirmation email"


def retry_pantheon_registration(modeladmin, request, queryset):
    """Re-attempt the Pantheon event enrollment for the selected registrations.

    Needed because re-saving an already approved registration does not re-fire the
    approval hook, so there is no other retry path after a Pantheon outage.
    """
    from mahjong_portal.notifications import confirmation_email
    from utils.new_pantheon import sync_registration_to_pantheon

    succeeded = 0
    failed = 0
    for registration in queryset:
        if sync_registration_to_pantheon(registration):
            succeeded += 1
            # the approval mail was withheld while the push was failing
            confirmation_email(registration)
        else:
            failed += 1
    modeladmin.message_user(
        request,
        f"Pantheon push: {succeeded} succeeded, {failed} skipped or failed.",
        level=messages.SUCCESS if not failed else messages.WARNING,
    )


retry_pantheon_registration.short_description = "Retry Pantheon event registration"


def mark_as_paid(modeladmin, request, queryset):
    """Mark the selected registrations as having paid; only for tournaments with an entry fee."""
    eligible = queryset.filter(tournament__entry_fee=True)
    updated = eligible.update(has_paid=True)
    skipped = queryset.count() - eligible.count()
    modeladmin.message_user(
        request,
        f"Marked {updated} registration(s) as paid. Skipped {skipped} without an entry fee tournament.",
        level=messages.SUCCESS if not skipped else messages.WARNING,
    )


mark_as_paid.short_description = "Player has paid (entry fee)"


def add_to_waitlist(modeladmin, request, queryset):
    """Put the selected registrations on their tournament's waitlist, numbered per tournament.

    Approved players are skipped: approving is what promotes somebody off the waitlist, so a
    row cannot be in both lists. Demote first (untick approval), then waitlist.
    """
    added = 0
    mailed = 0
    next_number = {}
    for registration in queryset.filter(is_approved=False, waitlist_number__isnull=True).order_by("created_on"):
        tournament_id = registration.tournament_id
        if tournament_id not in next_number:
            highest = TournamentRegistration.objects.filter(tournament_id=tournament_id).aggregate(
                Max("waitlist_number")
            )
            next_number[tournament_id] = (highest["waitlist_number__max"] or 0) + 1
        # queryset update: keeps the approval hook out of it
        TournamentRegistration.objects.filter(pk=registration.pk).update(waitlist_number=next_number[tournament_id])
        registration.waitlist_number = next_number[tournament_id]
        next_number[tournament_id] += 1
        added += 1
        if waitlist_email(registration):
            mailed += 1

    skipped = queryset.count() - added
    modeladmin.message_user(
        request,
        f"Added {added} registration(s) to the waitlist, emailed {mailed}. "
        f"Skipped {skipped} (already approved or already listed).",
        level=messages.SUCCESS if not skipped else messages.WARNING,
    )


add_to_waitlist.short_description = "Add to waitlist..."


def remove_from_waitlist(modeladmin, request, queryset):
    """Take the selected registrations off the waitlist. Remaining numbers keep their gaps."""
    removed = queryset.filter(waitlist_number__isnull=False).update(waitlist_number=None)
    modeladmin.message_user(request, f"Removed {removed} registration(s) from the waitlist.", level=messages.SUCCESS)


remove_from_waitlist.short_description = "Remove from waitlist..."


class TournamentEmailTemplateInline(admin.StackedInline):
    model = TournamentEmailTemplate
    extra = 0


def load_pantheon_results(modeladmin, request, queryset):
    """
    Load tournament results from a linked Pantheon event.
    Creates TournamentResult entries for all players in the Pantheon rating table.
    Players without a linked portal account are saved with load_player=false (player_string only).
    """
    if queryset.count() != 1:
        modeladmin.message_user(
            request,
            "Please select exactly one tournament to load Pantheon results for.",
            level=messages.WARNING,
        )
        return

    tournament = queryset.first()

    if not tournament.new_pantheon_id:
        modeladmin.message_user(
            request,
            f"Tournament {tournament.name!r} has no New Pantheon ID set. Cannot load results.",
            level=messages.ERROR,
        )
        return

    try:
        response = get_rating_table(tournament.new_pantheon_id)
        players_in_rating = response.list
    except Exception as e:
        modeladmin.message_user(
            request,
            f"Failed to fetch results from Pantheon: {e}",
            level=messages.ERROR,
        )
        return

    if not players_in_rating:
        modeladmin.message_user(
            request,
            "Pantheon returned an empty rating table for this event.",
            level=messages.WARNING,
        )
        return

    # Track stats
    created_count = 0
    updated_count = 0
    unlinked_count = 0

    with transaction.atomic():
        for place, entry in enumerate(players_in_rating, start=1):
            pantheon_id = entry.id
            title = entry.title
            scores = round(entry.rating, 2)
            games = entry.games_played

            # Try to find a linked portal player
            player = None
            try:
                player = Player.objects.get(pantheon_id=pantheon_id)
            except Player.DoesNotExist:
                unlinked_count += 1

            # Check if result already exists
            result, created = TournamentResult.objects.update_or_create(
                tournament=tournament,
                place=place,
                defaults={
                    "player": player,
                    "player_string": title if player is None else "",
                    "scores": scores,
                    "games": games,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

    modeladmin.message_user(
        request,
        f"Loaded {len(players_in_rating)} results from Pantheon event {tournament.new_pantheon_id}. "
        f"Created: {created_count}, Updated: {updated_count}, Unlinked players: {unlinked_count}.",
        level=messages.SUCCESS,
    )


load_pantheon_results.short_description = "Load Pantheon results"


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        exclude = ["registration_description", "results_description"]
        widgets = {
            "general_information": TinyMCE(),
            "venue_address": TinyMCE(),
            "schedule": TinyMCE(),
            "lunch_options": TinyMCE(),
            "contact_info": TinyMCE(),
        }


class TournamentAdmin(TranslationAdmin):
    form = TournamentForm

    prepopulated_fields = {"slug": ["name"]}
    list_display = ["name", "country", "end_date", "is_upcoming", "export"]
    list_filter = ["is_event", "tournament_type", "country"]
    search_fields = ["name"]

    ordering = ["-end_date"]

    filter_horizontal = ["clubs", "non_playing_organizers"]
    actions = [load_pantheon_results, send_registrant_email, send_email_to_all]
    inlines = [TournamentEmailTemplateInline]

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
                    "entry_fee",
                    "show_online_rank",
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
                    "non_playing_organizers",
                ]
            },
        ),
        (
            "Tournament Info Tab",
            {
                "fields": [
                    "general_information",
                    "venue_address",
                    "schedule",
                    "lunch_options",
                    "contact_info",
                    "organizer_emails",
                ]
            },
        ),
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
        "has_paid",
        "waitlist_number",
        "tournament",
        "first_name",
        "last_name",
        "city",
        "registration_country",
        "email",
        "phone",
        "ema_id",
        "player",
        "city_object",
        "allow_to_save_data",
        "created_on",
        "pantheon_synced_on",
        "pantheon_sync_error",
    ]

    raw_id_fields = ["tournament", "player", "city_object", "user"]
    list_filter = [["tournament", admin.RelatedOnlyFieldListFilter], "has_paid", "created_on"]
    readonly_fields = ["created_on"]
    actions = [
        approve_and_send_confirmation,
        retry_pantheon_registration,
        mark_as_paid,
        add_to_waitlist,
        remove_from_waitlist,
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        # ponytail: hidden only when no tournament at all has an entry fee; the action itself skips the rest.
        if "mark_as_paid" in actions and not Tournament.objects.filter(entry_fee=True).exists():
            del actions["mark_as_paid"]
        return actions


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
        "created_on",
    ]

    raw_id_fields = ["tournament", "player", "city_object", "user"]
    list_filter = [["tournament", admin.RelatedOnlyFieldListFilter], "created_on"]
    readonly_fields = ["created_on"]
    actions = [approve_and_send_confirmation]


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
        "created_on",
    ]

    raw_id_fields = ["tournament", "player", "city_object", "user"]
    list_filter = [["tournament", admin.RelatedOnlyFieldListFilter], "created_on"]
    readonly_fields = ["created_on"]
    actions = [approve_and_send_confirmation]


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
        general_information_de=app.general_information_de or None,
        general_information_en=app.general_information_en or None,
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
        f"Tournament {tournament.name!r} created. Please review and complete the details.",
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
