# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _
from twirp.context import Context

import pantheon_api.atoms_pb2
import pantheon_api.frey_pb2
import pantheon_api.mimir_pb2
from online.models import TournamentPlayers
from pantheon_api.frey_twirp import FreyClient
from pantheon_api.mimir_twirp import MimirClient

logger = logging.getLogger()


def get_new_pantheon_swiss_sortition(pantheonEventId, adminPersonId):
    client = MimirClient(settings.PANTHEON_NEW_API_URL)

    context = Context()
    # todo pass pantheon event's owner token
    context.set_header("X-Auth-Token", settings.PANTHEON_ADMIN_COOKIE)
    context.set_header("X-Current-Event-Id", str(pantheonEventId))
    context.set_header("X-Current-Person-Id", str(adminPersonId))

    return client.GenerateSwissSeating(
        ctx=context,
        request=pantheon_api.mimir_pb2.SeatingGenerateSwissSeatingPayload(
            event_id=int(pantheonEventId), substitute_replacement_players=True
        ),
        server_path_prefix="/v2",
    )


def get_pantheon_public_person_information(personId, email):
    client = FreyClient(settings.PANTHEON_AUTH_API_URL)

    response = client.GetPersonalInfo(
        ctx=Context(),
        request=pantheon_api.frey_pb2.PersonsGetPersonalInfoPayload(ids=[personId]),
        server_path_prefix="/v2",
    )
    person = response.people[0]

    return {
        "person_id": person.id,
        "country": person.country,
        "city": person.city,
        "tenhou_id": person.tenhou_id,
        "title": person.title,
        "has_avatar": person.has_avatar,
        "ms_nickname": person.ms_nickname,
        "ms_account_id": person.ms_account_id,
        "email": email,
    }


def update_personal_info(person_info, adminPersonId, pantheonEventId, isMajsoulTournament):
    client = FreyClient(settings.PANTHEON_AUTH_API_URL)
    context = Context()
    # todo pass pantheon event's owner token
    context.set_header("X-Auth-Token", settings.PANTHEON_ADMIN_COOKIE)
    context.set_header("X-Current-Event-Id", str(pantheonEventId))
    context.set_header("X-Current-Person-Id", str(adminPersonId))

    if not isMajsoulTournament:
        return client.UpdatePersonalInfo(
            ctx=context,
            request=pantheon_api.frey_pb2.PersonsUpdatePersonalInfoPayload(
                id=int(person_info["person_id"]),
                email=str(person_info["email"]),
                tenhou_id=str(person_info["tenhou_id"]),
                title=str(person_info["title"]),
                city=str(person_info["city"]),
                country=str(person_info["country"]),
                has_avatar=bool(person_info["has_avatar"]),
            ),
            server_path_prefix="/v2",
        )
    else:
        return client.UpdatePersonalInfo(
            ctx=context,
            request=pantheon_api.frey_pb2.PersonsUpdatePersonalInfoPayload(
                id=int(person_info["person_id"]),
                email=str(person_info["email"]),
                ms_nickname=str(person_info["ms_nickname"]),
                ms_friend_id=int(person_info["ms_friend_id"]),
                ms_account_id=int(person_info["ms_account_id"]),
                title=str(person_info["title"]),
                city=str(person_info["city"]),
                country=str(person_info["country"]),
                has_avatar=bool(person_info["has_avatar"]),
            ),
            server_path_prefix="/v2",
        )


def register_player(adminPersonId, pantheonEventId, pantheonId):
    client = MimirClient(settings.PANTHEON_NEW_API_URL)

    context = Context()
    # todo pass pantheon event's owner token
    context.set_header("X-Auth-Token", settings.PANTHEON_ADMIN_COOKIE)
    context.set_header("X-Current-Event-Id", str(pantheonEventId))
    context.set_header("X-Current-Person-Id", str(adminPersonId))

    return client.RegisterPlayer(
        ctx=context,
        request=pantheon_api.mimir_pb2.EventsRegisterPlayerPayload(
            event_id=int(pantheonEventId), player_id=int(pantheonId)
        ),
        server_path_prefix="/v2",
        timeout=30,
    )


def sync_registration_to_pantheon(registration) -> bool:
    """Enroll an approved offline+pantheon registrant in the linked Pantheon event.

    Never raises and never rolls back the portal registration; returns True only on a
    successful push. Failures are logged, stored on the registration and emailed to the
    organizers so somebody can enroll the player by hand.
    """
    tournament = registration.tournament

    if not registration.is_approved:
        return False
    if not tournament.is_pantheon_registration or tournament.is_online():
        return False
    if not tournament.new_pantheon_id:
        return False
    if registration.pantheon_synced_on:
        return False

    person_id = registration.user and registration.user.new_pantheon_id
    if not person_id:
        return _pantheon_sync_failed(registration, "No Pantheon account linked to this registration")

    if not settings.PANTHEON_ADMIN_ID:
        return _pantheon_sync_failed(registration, "PANTHEON_ADMIN_ID is not configured")

    try:
        register_player(settings.PANTHEON_ADMIN_ID, tournament.new_pantheon_id, person_id)
    except Exception as e:  # noqa: BLE001
        logger.exception("Pantheon registration push failed for registration %s", registration.pk)
        return _pantheon_sync_failed(registration, str(e))

    _store_pantheon_sync_state(registration, pantheon_synced_on=timezone.now(), pantheon_sync_error="")
    return True


def _pantheon_sync_failed(registration, reason) -> bool:
    from mahjong_portal.notifications import notify_pantheon_sync_failure

    logger.error("Pantheon registration push failed for registration %s: %s", registration.pk, reason)
    _store_pantheon_sync_state(registration, pantheon_sync_error=reason)
    notify_pantheon_sync_failure(registration, reason)
    return False


def _store_pantheon_sync_state(registration, **fields):
    # queryset update, not save(): this runs from inside save() and would recurse
    type(registration).objects.filter(pk=registration.pk).update(**fields)
    for name, value in fields.items():
        setattr(registration, name, value)


def add_user_to_new_pantheon(
    record: TournamentPlayers, registration, pantheonEventId, adminPersonId, isMajsoulTournament
):
    if not registration.user or not registration.user.email:
        return _("There is no user email in the registration."), False

    person_info = get_pantheon_public_person_information(record.pantheon_id, registration.user.email)

    if isMajsoulTournament:
        person_info["ms_nickname"] = registration.ms_nickname
        person_info["ms_account_id"] = registration.ms_account_id
        person_info["ms_friend_id"] = registration.ms_friend_id
    else:
        person_info["tenhou_id"] = registration.tenhou_nickname
        person_info["ms_friend_id"] = -1

    # todo: check update person errors
    update_personal_info(person_info, adminPersonId, pantheonEventId, isMajsoulTournament)
    # todo: check register player error
    register_player(adminPersonId, pantheonEventId, record.pantheon_id)
    return "Success", True


def upload_replay_through_pantheon(eventId, platformId, contentType, replayHash, logTime, content):
    client = MimirClient(settings.PANTHEON_NEW_API_URL)

    context = Context()
    context.set_header("HTTP-X-EXTERNAL-QUERY-SECRET", settings.EXTERNAL_QUERY_SECRET)

    return client.AddTypedOnlineReplay(
        ctx=context,
        request=pantheon_api.mimir_pb2.TypedGamesAddOnlineReplayPayload(
            event_id=int(eventId),
            platform_id=int(platformId),
            content_type=int(contentType),
            log_timestamp=int(logTime),
            replay_hash=str(replayHash),
            content=content,
        ),
        server_path_prefix="/v2",
    )


def add_online_replay_through_pantheon(eventId, tenhouGameLink):
    client = MimirClient(settings.PANTHEON_NEW_API_URL)

    context = Context()
    context.set_header("HTTP-X-EXTERNAL-QUERY-SECRET", settings.EXTERNAL_QUERY_SECRET)

    return client.AddOnlineReplay(
        ctx=context,
        request=pantheon_api.mimir_pb2.GamesAddOnlineReplayPayload(
            event_id=int(eventId),
            link=str(tenhouGameLink),
        ),
        server_path_prefix="/v2",
    )


def add_penalty_game(pantheonEventId, adminPersonId, playerIds):
    client = MimirClient(settings.PANTHEON_NEW_API_URL)

    context = Context()
    # todo pass pantheon event's owner token
    context.set_header("X-Auth-Token", settings.PANTHEON_ADMIN_COOKIE)
    context.set_header("X-Current-Event-Id", str(pantheonEventId))
    context.set_header("X-Current-Person-Id", str(adminPersonId))

    return client.AddPenaltyGame(
        ctx=context,
        request=pantheon_api.mimir_pb2.GamesAddPenaltyGamePayload(event_id=int(pantheonEventId), players=playerIds),
        server_path_prefix="/v2",
    )


def send_team_names_to_pantheon(pantheonEventId, adminPersonId, teamMapping):
    client = MimirClient(settings.PANTHEON_NEW_API_URL)

    context = Context()
    # todo pass pantheon event's owner token
    context.set_header("X-Auth-Token", settings.PANTHEON_ADMIN_COOKIE)
    context.set_header("X-Current-Event-Id", str(pantheonEventId))
    context.set_header("X-Current-Person-Id", str(adminPersonId))

    teams = []
    for team in teamMapping:
        teams.append(
            pantheon_api.atoms_pb2.TeamMapping(player_id=int(team["player_id"]), team_name=str(team["team_name"]))
        )

    return client.UpdatePlayersTeams(
        ctx=context,
        request=pantheon_api.mimir_pb2.EventsUpdatePlayersTeamsPayload(
            event_id=int(pantheonEventId), ids_to_team_names=teams
        ),
        server_path_prefix="/v2",
    )


def get_rating_table(eventId):
    client = MimirClient(settings.PANTHEON_NEW_API_URL)

    context = Context()
    context.set_header("HTTP-X-EXTERNAL-QUERY-SECRET", settings.EXTERNAL_QUERY_SECRET)

    return client.GetRatingTable(
        ctx=context,
        request=pantheon_api.mimir_pb2.EventsGetRatingTablePayload(
            event_id_list=[int(eventId)], order_by="rating", order="desc"
        ),
        server_path_prefix="/v2",
    )
