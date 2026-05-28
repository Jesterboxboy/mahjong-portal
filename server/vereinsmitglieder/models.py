# -*- coding: utf-8 -*-

from django.db import models


class Mitgliedschaftsbeitrag(models.Model):
    year = models.PositiveIntegerField(verbose_name="Jahr")
    player = models.ForeignKey(
        "player.Player",
        on_delete=models.CASCADE,
        related_name="membership_fees",
        verbose_name="Spieler",
    )

    class Meta:
        verbose_name = "Mitgliedschaftsbeitrag"
        verbose_name_plural = "Mitgliedschaftsbeiträge"
        unique_together = [["year", "player"]]
        ordering = ["-year", "player__last_name", "player__first_name"]

    def __str__(self):
        return f"{self.year} — {self.player.last_name}, {self.player.first_name}"
