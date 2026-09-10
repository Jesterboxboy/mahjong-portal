# -*- coding: utf-8 -*-

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from account.models import PantheonInfoUpdateLog
from mahjong_portal.notifications import notify_organizers_new_registration
from pantheon_api.api_calls.user import get_pantheon_public_person_information
from player.models import Player
from player.player_helper import PlayerHelper
from settings.models import City, Country
from tournament.forms import (
    MajsoulOnlineTournamentPantheonRegistrationForm,
    OnlineTournamentPantheonRegistrationForm,
    OnlineTournamentRegistrationForm,
    TournamentApplicationForm,
    TournamentRegistrationForm,
)
from tournament.models import (
    MsOnlineTournamentRegistration,
    OnlineTournamentRegistration,
    Tournament,
    TournamentRegistration,
    TournamentResult,
)
from utils.general import get_end_of_day, get_random_confirm_code, split_name

logger = logging.getLogger(__name__)


def tournament_list(request, tournament_type=None, year=None):
    current_year = timezone.now().year
    try:
        selected_year = year and int(year)
    except ValueError:
        selected_year = current_year

    years = []
    for x in range(10):
        years.append(current_year - x)

    tournaments = Tournament.objects.filter(end_date__year=selected_year)

    if tournament_type == "ema":
        tournament_types = [Tournament.EMA]
        tournaments = tournaments.filter(tournament_type__in=tournament_types)
    else:
        tournament_types = [Tournament.EMA, Tournament.OTHER, Tournament.ONLINE]
        tournaments = tournaments.filter(tournament_type__in=tournament_types)

    tournaments = tournaments.order_by("-end_date").prefetch_related("city").prefetch_related("country")

    current_date = get_end_of_day()
    all_tournaments = (
        Tournament.public.filter(is_upcoming=True)
        .filter(is_event=False)
        .prefetch_related("city")
        .order_by("start_date", "name")
    )

    current_tournaments = all_tournaments.filter(start_date__lte=current_date)
    upcoming_tournaments = all_tournaments.filter(start_date__gt=current_date)
    tournaments = tournaments.filter(is_upcoming=False)

    return render(
        request,
        "tournament/list.html",
        {
            "tournaments": tournaments,
            "current_tournaments": current_tournaments,
            "upcoming_tournaments": upcoming_tournaments,
            "tournament_type": tournament_type,
            "years": years,
            "selected_year": selected_year,
            "page": tournament_type or "tournament",
        },
    )


def tournament_details(request, slug):
    tournament = get_object_or_404(Tournament, slug=slug)
    if tournament.is_upcoming:
        return redirect(tournament_announcement, slug=slug)

    results = (
        TournamentResult.objects.filter(tournament=tournament)
        .order_by("place")
        .prefetch_related("player__city")
        .prefetch_related("player__country")
        .prefetch_related("player")
    )

    countries = {}
    for result in results:
        if not result.player:
            continue

        country = result.player.country
        if not country:
            continue

        if not countries.get(country.id):
            countries[country.id] = {"count": 0, "name": country.name, "code": country.code}

        countries[country.id]["count"] += 1

    countries = sorted(countries.values(), key=lambda x: x["count"], reverse=True)

    has_multiple_countries = len(countries) > 1

    return render(
        request,
        "tournament/details.html",
        {
            "tournament": tournament,
            "results": results,
            "page": "tournament",
            "countries": countries,
            "has_multiple_countries": has_multiple_countries,
        },
    )


def _last_known_pantheon_phone(user):
    """Phone as captured at the user's last login.

    Frey only exposes a phone number to the authenticated `Me()` call, so the public
    person lookup never has it. The login snapshot in PantheonInfoUpdateLog is the only
    copy the portal ever sees; it may be stale until the user logs in again.
    """
    log = (
        PantheonInfoUpdateLog.objects.filter(user=user, updated_information__has_key="phone")
        .exclude(updated_information__phone="")
        .order_by("-created_on")
        .first()
    )
    return log and log.updated_information.get("phone") or ""


def pantheon_registration_initial(user):
    """Best-effort Pantheon prefill; returns only the keys that have a value."""
    if not user.new_pantheon_id:
        return {}

    try:
        data = get_pantheon_public_person_information(user.new_pantheon_id)
    except Exception:  # noqa: BLE001
        # a Pantheon outage must not break the announcement page
        logger.exception("Could not load Pantheon data for user %s", user.pk)
        return {}

    first_name, last_name = split_name(data.get("title") or "")

    country_code = data.get("country") or ""
    country = Country.objects.filter(code__iexact=country_code).first()

    initial = {
        "first_name": first_name,
        "last_name": last_name,
        "city": data.get("city") or "",
        "registration_country": country and country.name or country_code,
        "email": user.email,
        "phone": _last_known_pantheon_phone(user),
    }
    return {key: value for key, value in initial.items() if value}


def tournament_announcement(request, slug):
    tournament = get_object_or_404(Tournament, slug=slug)

    initial = {"tournament": tournament}
    if tournament.city and tournament.fill_city_in_registration:
        initial["city"] = tournament.city.name

    if (
        tournament.is_pantheon_registration
        and not tournament.is_online()
        and tournament.opened_registration
        and request.user.is_authenticated
    ):
        initial.update(pantheon_registration_initial(request.user))

    if tournament.is_online():
        if tournament.is_majsoul_tournament and tournament.is_pantheon_registration:
            form = MajsoulOnlineTournamentPantheonRegistrationForm(initial=initial)
        elif not tournament.is_majsoul_tournament and tournament.is_pantheon_registration:
            form = OnlineTournamentPantheonRegistrationForm(initial=initial)
        else:
            form = OnlineTournamentRegistrationForm(initial=initial)
    else:
        form = TournamentRegistrationForm(initial=initial)

    full_approved_players_count = 0
    if tournament.is_online():
        if tournament.is_majsoul_tournament:
            registration_results = (
                MsOnlineTournamentRegistration.objects.filter(tournament=tournament)
                .filter(is_approved=True)
                .prefetch_related("player")
                .prefetch_related("city_object")
                .order_by("created_on")
            )
            full_approved_players_count = registration_results.filter(is_highlighted=True).count()
        else:
            registration_results = (
                OnlineTournamentRegistration.objects.filter(tournament=tournament)
                .filter(is_approved=True)
                .prefetch_related("player")
                .prefetch_related("city_object")
                .order_by("created_on")
            )
            full_approved_players_count = registration_results.filter(is_highlighted=True).count()
        if tournament.display_notes:
            registration_results = registration_results.order_by("notes", "created_on")
    else:
        registration_results = (
            TournamentRegistration.objects.filter(tournament=tournament)
            .filter(is_approved=True)
            .prefetch_related("player")
            .prefetch_related("city_object")
            .order_by("created_on")
        )
        full_approved_players_count = registration_results.filter(is_highlighted=True).count()
        if tournament.display_notes:
            registration_results = registration_results.order_by("notes", "created_on")

    is_already_registered = False
    registration_confirm_code = None
    if request.user.is_authenticated:
        if tournament.is_majsoul_tournament:
            current_registration = MsOnlineTournamentRegistration.objects.filter(
                tournament=tournament, user=request.user, is_approved=True
            )
            is_already_registered = current_registration.exists()
            if is_already_registered:
                registration_confirm_code = current_registration[0].confirm_code
        elif tournament.is_online():
            current_registration = OnlineTournamentRegistration.objects.filter(
                tournament=tournament, user=request.user, is_approved=True
            )
            is_already_registered = current_registration.exists()
            if is_already_registered:
                registration_confirm_code = current_registration[0].confirm_code
        elif tournament.is_pantheon_registration:
            # not filtered by is_approved: a pending row must still hide the form,
            # otherwise the user re-submits and creates duplicates
            is_already_registered = TournamentRegistration.objects.filter(
                tournament=tournament, user=request.user
            ).exists()

    missed_tenhou_id_error = request.GET.get("error") == "tenhou_id"
    form_data_error = request.GET.get("error") == "form_data"

    return render(
        request,
        "tournament/announcement.html",
        {
            "tournament": tournament,
            "page": "tournament",
            "form": form,
            "registration_results": registration_results,
            "is_already_registered": is_already_registered,
            "missed_tenhou_id_error": missed_tenhou_id_error,
            "form_data_error": form_data_error,
            "full_approved_players_count": full_approved_players_count,
            "registration_confirm_code": registration_confirm_code,
        },
    )


@require_POST
@login_required
def pantheon_tournament_registration(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    # offline pantheon tournaments go through tournament_registration instead
    if not tournament.is_online():
        return redirect(tournament.get_url())

    user = request.user
    form_data = request.POST
    notes = None

    if tournament.display_notes:
        notes = form_data["notes"]

    if tournament.is_majsoul_tournament:
        try:
            ms_friend_id = int(form_data["ms_friend_id"])
            ms_nickname = form_data["ms_nickname"]
            if form_data.get("allow_to_save_data") is None:
                allow_to_save_data = False
            else:
                allow_to_save_data = bool(form_data["allow_to_save_data"])
            if not bool(ms_nickname.strip()):
                return redirect(tournament.get_url() + "?error=form_data")
        except Exception:
            return redirect(tournament.get_url() + "?error=form_data")

    if tournament.is_majsoul_tournament:
        if MsOnlineTournamentRegistration.objects.filter(user=user, tournament=tournament).exists():
            return redirect(tournament.get_url())
    else:
        if OnlineTournamentRegistration.objects.filter(user=user, tournament=tournament).exists():
            return redirect(tournament.get_url())

    # todo get ms_data and store into PantheonInfoUpdateLog
    data = get_pantheon_public_person_information(user.new_pantheon_id)
    PantheonInfoUpdateLog.objects.create(user=user, pantheon_id=user.new_pantheon_id, updated_information=data)
    full_name = data["title"]
    first_name, last_name = split_name(full_name)

    player = PlayerHelper.find_player_smart(player_full_name=full_name)
    city_object = City.objects.filter(name=data["city"].title()).first()

    if not tournament.is_majsoul_tournament and not data["tenhou_id"]:
        return redirect(tournament.get_url() + "?error=tenhou_id")

    player_is_approved = True
    if tournament.registrations_pre_moderation:
        player_is_approved = False
        message = _("Your registration was accepted! It will be visible on the page after administrator approvement.")

        messages.success(request, message)

    confirm_code = None
    if tournament.is_online() and tournament.with_confirm_code:
        confirm_code = get_random_confirm_code()

    if tournament.is_majsoul_tournament:
        # todo get ms_data from pantheon
        registration = MsOnlineTournamentRegistration.objects.create(
            tournament=tournament,
            user=user,
            ms_nickname=ms_nickname,
            ms_friend_id=ms_friend_id,
            first_name=first_name,
            last_name=last_name,
            city=data["city"],
            player=player,
            city_object=city_object,
            allow_to_save_data=allow_to_save_data,
            notes=notes,
            is_approved=player_is_approved,
            confirm_code=confirm_code,
        )
    else:
        registration = OnlineTournamentRegistration.objects.create(
            tournament=tournament,
            user=user,
            tenhou_nickname=data["tenhou_id"],
            first_name=first_name,
            last_name=last_name,
            city=data["city"],
            player=player,
            city_object=city_object,
            notes=notes,
            is_approved=player_is_approved,
            confirm_code=confirm_code,
        )

    notify_organizers_new_registration(registration)

    return redirect(tournament.get_url())


@require_POST
def tournament_registration(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if tournament.is_online():
        form = OnlineTournamentRegistrationForm(request.POST, initial={"tournament": tournament})
    else:
        form = TournamentRegistrationForm(request.POST, initial={"tournament": tournament})

    if form.is_valid():
        if tournament.is_pantheon_registration and not tournament.is_online():
            if not request.user.is_authenticated:
                return redirect(tournament.get_url())
            if TournamentRegistration.objects.filter(tournament=tournament, user=request.user).exists():
                return redirect(tournament.get_url())

        if tournament.is_online():
            tenhou_nickname = form.cleaned_data.get("tenhou_nickname")
            exists = OnlineTournamentRegistration.objects.filter(
                tournament=tournament, tenhou_nickname=tenhou_nickname
            ).exists()
            if exists:
                messages.success(request, _("You already registered to the tournament!"))
                return redirect(tournament.get_url())

        instance = form.save(commit=False)
        instance.tournament = tournament

        # it supports auto load objects only for Russian tournaments right now

        try:
            if instance.city:
                instance.city_object = City.objects.get(name=instance.city)
        except City.DoesNotExist:
            pass

        # an admin-approved account link beats guessing by name: Pantheon titles carry
        # middle names ("Michael Mike Gürtl-Dusleag") that find_player_smart cannot match
        attached_player = request.user.is_authenticated and request.user.attached_player
        if attached_player:
            instance.player = attached_player
        else:
            try:
                full_name = f"{instance.first_name.title()} {instance.last_name.title()}"
                if instance.city_object:
                    instance.player = PlayerHelper.find_player_smart(
                        player_full_name=full_name, city_object=instance.city_object
                    )
                else:
                    instance.player = PlayerHelper.find_player_smart(player_full_name=full_name)
                if not instance.player:
                    raise Player.DoesNotExist
            except (Player.DoesNotExist, Player.MultipleObjectsReturned):
                # TODO if multiple players are here, let's try to filter by city
                pass

        if tournament.registrations_pre_moderation:
            instance.is_approved = False
            message = _(
                "Your registration was accepted! It will be visible on the page after administrator approvement."
            )
        else:
            instance.is_approved = True
            message = _("Your registration was accepted!")

        if request.user.is_authenticated:
            instance.user = request.user

        instance.save()

        notify_organizers_new_registration(instance)

        messages.success(request, message)
    else:
        messages.success(request, _("Please, allow to store personal data"))

    return redirect(tournament.get_url())


def tournament_application(request):
    success = False
    form = TournamentApplicationForm()

    if request.POST:
        form = TournamentApplicationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                tournament_application = form.save(commit=False)
                if tournament_application is not None:
                    if "is_admin_myself" in request.POST and request.user is not None:
                        tournament_application.tournament_admin_user = request.user
                    tournament_application.save()
                success = True

    return render(request, "tournament/application.html", {"form": form, "success": success})
