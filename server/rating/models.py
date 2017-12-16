from django.db import models

from leaderboard.models import BaseModel
from player.models import Player
from tournament.models import Tournament


class Rating(BaseModel):
    INNER = 0
    EMA = 1
    TYPES = [
        [INNER, 'Inner'],
        [EMA, 'EMA']
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    type = models.PositiveSmallIntegerField(choices=TYPES)


class RatingDelta(BaseModel):
    rating = models.ForeignKey(Rating, on_delete=models.PROTECT)
    player = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='rating_delta')
    tournament = models.ForeignKey(Tournament, on_delete=models.PROTECT, related_name='rating_delta')
    delta = models.IntegerField()
    is_active = models.BooleanField(default=False)
