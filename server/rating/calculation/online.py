from player.models import Player
from rating.calculation.rr import RatingRRCalculation
from tournament.models import Tournament, TournamentResult


class RatingOnlineCalculation(RatingRRCalculation):
    TOURNAMENT_TYPES = [Tournament.ONLINE]

    SECOND_PART_MIN_TOURNAMENTS = 3

    def get_players(self):
        player_ids = TournamentResult.objects.filter(tournament__tournament_type=Tournament.ONLINE).values_list(
            "player_id", flat=True
        )
        return Player.objects.filter(id__in=player_ids).exclude(is_replacement=True).exclude(is_hide=True)
