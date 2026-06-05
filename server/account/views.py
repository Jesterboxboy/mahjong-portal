# -*- coding: utf-8 -*-
from urllib.parse import parse_qs, urlparse

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from account.forms import LoginForm
from account.models import AttachingPlayerRequest, PantheonInfoUpdateLog, User
from austria_ranking.models import EventAttendanceIntent, QuotaEvent
from player.models import Player
from player.player_helper import PlayerHelper
from player.tenhou.models import TenhouAggregatedStatistics


def do_login(request):
    form = LoginForm(initial={"next": request.GET.get("next", "/")})
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            pantheon_id = form.user_data["person_id"]
            try:
                user = User.objects.get(new_pantheon_id=pantheon_id)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=form.user_data["email"],
                    email=form.user_data["email"],
                    password=None,
                )
                user.new_pantheon_id = pantheon_id
                user.save()

            PantheonInfoUpdateLog.objects.create(user=user, pantheon_id=pantheon_id, updated_information=form.user_data)

            login(request, user)

            return redirect(form.cleaned_data["next"])

    return render(request, "account/login.html", {"form": form})


@csrf_protect
def account_settings(request):
    success = None
    error_code = None
    current_player = None
    current_tenhou_account = None
    player_search_results = None
    player_search_query = None
    player_search_performed = False
    pending_attach_request = None
    is_anonymous = request.user is not None and isinstance(request.user, AnonymousUser)
    if is_anonymous:
        return render(request, "access_denied.html", status=403)

    if request.user is not None and request.user.attached_player is not None:
        current_player = request.user.attached_player
        current_tenhou_account = current_player.tenhou_object

    if request.user.is_authenticated and not request.user.attached_player:
        pending_attach_request = AttachingPlayerRequest.objects.filter(user=request.user, is_processed=False).first()

    if request.POST:
        action = request.POST.get("action")

        if action == "search_player" and not request.user.attached_player:
            query = request.POST.get("player_search", "").strip()
            player_search_query = query
            player_search_performed = True
            if query:
                player_search_results = Player.objects.filter(
                    Q(first_name__icontains=query) | Q(last_name__icontains=query)
                ).order_by("last_name", "first_name")[:20]

        elif action == "create_attach_request" and not request.user.attached_player:
            player_id = request.POST.get("player_id")
            contacts = request.POST.get("contacts", "").strip()
            if player_id and contacts:
                try:
                    player = Player.objects.get(pk=player_id)
                    if not AttachingPlayerRequest.objects.filter(user=request.user, player=player, is_processed=False).exists():
                        AttachingPlayerRequest.objects.create(user=request.user, player=player, contacts=contacts)
                    messages.success(request, _("Your attach request was submitted. An admin will review and link your account."))
                    return redirect("account_settings")
                except Player.DoesNotExist:
                    messages.error(request, _("Player not found."))

        elif request.user is not None and not is_anonymous and request.user.is_authenticated:
            if current_player is not None and current_player.tenhou_object is not None:
                current_tenhou = current_player.tenhou_object
                current_tenhou_nickname = current_tenhou.tenhou_username
                if current_tenhou_nickname is not None:
                    log_url = request.POST.get("log_url")
                    if log_url is not None:
                        error_code, log_hash = get_replay_hash(log_url)
                        if error_code is None and log_hash is not None:
                            try:
                                stat = TenhouAggregatedStatistics.objects.get(
                                    game_players=TenhouAggregatedStatistics.FOUR_PLAYERS, tenhou_object=current_tenhou
                                )
                            except TenhouAggregatedStatistics.DoesNotExist:
                                stat = None
                            if stat is not None:
                                new_rating = PlayerHelper.calculate_rating(
                                    log_hash, current_tenhou_nickname, stat.played_games
                                )
                                if new_rating is not None:
                                    stat.rate = new_rating
                                    stat.save()
                                    success = True
                                else:
                                    success = False
                                    error_code = 2
                            else:
                                success = False
                                error_code = None
                        else:
                            success = False
                    else:
                        success = False
                        error_code = 1

    # Build attendance data for the settings page
    attendance_data = []
    if request.user.is_authenticated and not is_anonymous:
        existing_intents = {
            i.quota_period_id: i.status for i in EventAttendanceIntent.objects.filter(user=request.user)
        }
        for period in QuotaEvent.objects.all():
            attendance_data.append((period, existing_intents.get(period.pk, EventAttendanceIntent.UNKNOWN)))

    return render(
        request,
        "account/settings.html",
        {
            "success": success,
            "error_code": error_code,
            "player": current_player,
            "tenhou_account": current_tenhou_account,
            "attendance_data": attendance_data,
            "pending_attach_request": pending_attach_request,
            "player_search_results": player_search_results,
            "player_search_query": player_search_query,
            "player_search_performed": player_search_performed,
        },
    )


def get_replay_hash(log_link):
    # error_message = _("This is not looks like a link to the game log.")
    error_code = 1

    log_link = log_link.replace("https://", "http://")

    log_link = log_link.strip()
    if not log_link.startswith("http://tenhou.net/"):
        return error_code, None

    attributes = parse_qs(urlparse(log_link).query)

    if "log" not in attributes:
        return error_code, None

    log_id = attributes["log"][0]
    return None, log_id


@login_required
@require_POST
def request_player_and_user_connection(request, slug):
    player = get_object_or_404(Player, slug=slug)
    contacts = request.POST.get("contacts")
    if not contacts:
        return redirect("player_details", slug)

    AttachingPlayerRequest.objects.create(user=request.user, player=player, contacts=contacts)
    messages.success(request, _("Request was created."))
    return redirect("player_details", player.slug)


@login_required
@require_POST
def set_attendance_intent(request, period_pk: int):
    period = get_object_or_404(QuotaEvent, pk=period_pk)
    status = request.POST.get("status", EventAttendanceIntent.UNKNOWN)
    if status not in (
        EventAttendanceIntent.ATTENDING,
        EventAttendanceIntent.NOT_ATTENDING,
        EventAttendanceIntent.UNKNOWN,
    ):
        status = EventAttendanceIntent.UNKNOWN
    EventAttendanceIntent.objects.update_or_create(
        user=request.user,
        quota_period=period,
        defaults={"status": status},
    )
    return redirect("account_settings")
