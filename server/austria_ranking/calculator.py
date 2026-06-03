# -*- coding: utf-8 -*-
"""
Austrian riichi ranking calculation engine.

Formula (EMA standard):
  points = round(((A - R) / (A - 1)) * 1000)
  where A = number of players, R = player's rank (1-based).
  Last place (R == A) yields 0 and is discarded.

Final score per player:
  AT score     = sum of points for all Austrian tournaments
  foreign score = sum of top-3 points for non-Austrian tournaments
  total         = AT score + foreign score
"""

from austria_ranking.models import AustrianRanking, EmaTournamentResult
from player.models import Player
from vereinsmitglieder.models import Mitgliedschaftsbeitrag

ORGANIZER_BONUS_TOURNAMENT_NAME = "Veranstalter-Ø"


def calculate_points(player_count: int, position: int) -> int:
    """Return the ranking points for a given tournament result."""
    if player_count <= 1:
        return 0
    return round(((player_count - position) / (player_count - 1)) * 1000)


def _inject_organizer_bonuses(
    quota_period,
    player_data: dict,
    player_lookup: dict,
) -> None:
    """
    For each tournament in the quota period that has a non_playing_organizer,
    compute the average of that player's existing AT base points and inject a
    synthetic result (position 999) both into player_data (for scoring) and as
    a persisted EmaTournamentResult row (for the detail view).

    Only organizers who already have at least one AT result in the period
    receive the bonus (otherwise the average is undefined).
    """
    from tournament.models import Tournament as PortalTournament

    organizer_tournaments = (
        PortalTournament.objects.filter(
            non_playing_organizer__isnull=False,
            end_date__gte=quota_period.start_date,
            end_date__lte=quota_period.end_date,
        )
        .select_related("non_playing_organizer")
        .order_by("end_date")
    )

    # Track which organizer EMA IDs we've already processed (one bonus per player per period)
    processed: set[str] = set()

    for tournament in organizer_tournaments:
        organizer = tournament.non_playing_organizer
        if organizer is None or not organizer.ema_id:
            continue
        ema_id = organizer.ema_id
        if ema_id in processed:
            continue
        processed.add(ema_id)

        # Only give the bonus if the player has actual AT results in this period
        at_results = player_data.get(ema_id, {}).get("at_results", [])
        if not at_results:
            continue

        avg_points = round(sum(r["points"] for r in at_results) / len(at_results))
        if avg_points <= 0:
            continue

        bonus_name = tournament.name

        # Inject into in-memory player_data.
        # year=None bypasses the membership-fee year check since the bonus is
        # already derived from fee-validated actual results.
        player_data[ema_id]["at_results"].append(
            {
                "name": bonus_name,
                "points": avg_points,
                "year": None,
                "is_organizer_bonus": True,
            }
        )

        # Persist a synthetic EmaTournamentResult so the detail view can show it
        display_name: str = player_data[ema_id]["display_name"]
        parts = display_name.split(maxsplit=1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        EmaTournamentResult.objects.update_or_create(
            quota_period=quota_period,
            ema_id=ema_id,
            tournament_name=bonus_name,
            end_date=quota_period.end_date,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "tournament_country_code": "AT",
                "position": 999,
                "player_count": 1,
                "points": avg_points,
                "is_austrian_tournament": True,
            },
        )


def rank_players_for_period(quota_period) -> list[dict]:
    """
    Calculate and persist AustrianRanking rows for the given QuotaEvent.

    Returns the sorted ranking list as a list of dicts (for immediate use in views/admin).
    """
    # Remove stale organizer-bonus synthetic rows so they don't double-count
    EmaTournamentResult.objects.filter(
        quota_period=quota_period,
        position=999,
    ).delete()

    results = EmaTournamentResult.objects.filter(quota_period=quota_period, points__gt=0)

    # Group by ema_id
    player_data: dict[str, dict] = {}
    for r in results:
        if r.ema_id not in player_data:
            player_data[r.ema_id] = {
                "ema_id": r.ema_id,
                "display_name": f"{r.first_name} {r.last_name}",
                "at_results": [],
                "foreign_results": [],
            }
        if r.is_austrian_tournament:
            player_data[r.ema_id]["at_results"].append(
                {"name": r.tournament_name, "points": r.points, "year": r.end_date.year if r.end_date else None}
            )
        else:
            player_data[r.ema_id]["foreign_results"].append(
                {"name": r.tournament_name, "points": r.points, "year": r.end_date.year if r.end_date else None}
            )

    # Build player → portal Player lookup by ema_id
    ema_ids = list(player_data.keys())
    player_lookup: dict[str, Player] = {p.ema_id: p for p in Player.objects.filter(ema_id__in=ema_ids) if p.ema_id}

    # Build paid-years lookup:
    # - ema_id in lookup → player is in the portal; only years in the set are counted
    # - ema_id absent → player is not in the portal; no fee restriction (can't be managed)
    player_pk_to_ema: dict[int, str] = {p.pk: ema_id for ema_id, p in player_lookup.items()}
    paid_years_lookup: dict[str, set[int]] = {ema_id: set() for ema_id in player_lookup}
    for fee in Mitgliedschaftsbeitrag.objects.filter(player_id__in=player_pk_to_ema.keys()):
        ema_id = player_pk_to_ema[fee.player_id]
        paid_years_lookup[ema_id].add(fee.year)

    # ── Organizer bonus ─────────────────────────────────────────────────────
    # A player set as non_playing_organizer on an Austrian tournament within the
    # quota period receives the average of their existing AT base points for the
    # period added as a synthetic result (position 999).
    _inject_organizer_bonuses(quota_period, player_data, player_lookup)
    # ────────────────────────────────────────────────────────────────────────

    # Score each player
    rankings = []
    for ema_id, data in player_data.items():
        # None → player not in portal → no fee restriction; set → only those years count
        portal_paid_years = paid_years_lookup.get(ema_id)

        def _year_ok(result_item, _ppy=portal_paid_years):
            if _ppy is None:
                return True  # not a portal player → no fee tracking
            year = result_item.get("year")
            return year is None or year in _ppy

        at_points = sum(r["points"] for r in data["at_results"] if _year_ok(r))
        top3_foreign = sorted(
            [r for r in data["foreign_results"] if _year_ok(r)],
            key=lambda x: x["points"],
            reverse=True,
        )[:3]
        foreign_points = sum(r["points"] for r in top3_foreign)
        total_points = at_points + foreign_points
        rankings.append(
            {
                "ema_id": ema_id,
                "display_name": data["display_name"],
                "at_points": at_points,
                "foreign_points": foreign_points,
                "total_points": total_points,
                "at_results": data["at_results"],
                "foreign_results": top3_foreign,
                "portal_player": player_lookup.get(ema_id),
            }
        )

    rankings.sort(key=lambda x: x["total_points"], reverse=True)

    # Persist to AustrianRanking, replacing any existing rows for this period
    AustrianRanking.objects.filter(quota_period=quota_period).delete()
    for pos, row in enumerate(rankings, start=1):
        AustrianRanking.objects.create(
            quota_period=quota_period,
            player=row["portal_player"],
            ema_id=row["ema_id"],
            display_name=row["display_name"],
            rank_position=pos,
            total_points=row["total_points"],
            at_points=row["at_points"],
            foreign_points=row["foreign_points"],
        )

    return rankings
