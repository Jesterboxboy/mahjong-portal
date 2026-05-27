# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models

from player.models import Player


class QuotaEvent(models.Model):
    WM = "wm"
    EM = "em"
    EVENT_TYPE_CHOICES = [
        (WM, "WM (WRC)"),
        (EM, "EM (ERMC)"),
    ]

    name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=2, choices=EVENT_TYPE_CHOICES, default=WM)
    start_date = models.DateField()
    end_date = models.DateField()
    calculated_at = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    seats_available = models.PositiveIntegerField(null=True, blank=True, help_text="If set, the first N confirmed-attending players earn a guaranteed seat (shown with ✓ in the ranking).")

    class Meta:
        ordering = ["-end_date"]
        verbose_name = "Quota Event"
        verbose_name_plural = "Quota Events"

    def __str__(self):
        return self.name


# Keep backward-compatible alias so existing code can still import QuotaPeriod
QuotaPeriod = QuotaEvent


class EmaTournamentResult(models.Model):
    quota_period = models.ForeignKey(QuotaPeriod, on_delete=models.CASCADE, related_name="ema_results")
    ema_id = models.CharField(max_length=30)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    tournament_name = models.CharField(max_length=255)
    tournament_country_code = models.CharField(max_length=2)
    end_date = models.DateField()
    position = models.PositiveIntegerField()
    player_count = models.PositiveIntegerField()
    points = models.PositiveIntegerField(default=0)
    is_austrian_tournament = models.BooleanField(default=False)
    ema_tournament_url = models.URLField(blank=True, default="")

    class Meta:
        ordering = ["-end_date"]
        verbose_name = "EMA Tournament Result"
        verbose_name_plural = "EMA Tournament Results"
        unique_together = [("quota_period", "ema_id", "tournament_name", "end_date")]

    def __str__(self):
        return f"{self.first_name} {self.last_name} – {self.tournament_name} ({self.end_date})"


class AustrianRanking(models.Model):
    quota_period = models.ForeignKey(QuotaPeriod, on_delete=models.CASCADE, related_name="rankings")
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="austria_rankings")
    ema_id = models.CharField(max_length=30)
    display_name = models.CharField(max_length=200)
    rank_position = models.PositiveIntegerField()
    total_points = models.PositiveIntegerField(default=0)
    at_points = models.PositiveIntegerField(default=0)
    foreign_points = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["rank_position"]
        verbose_name = "Austrian Ranking"
        verbose_name_plural = "Austrian Rankings"

    def __str__(self):
        return f"#{self.rank_position} {self.display_name} ({self.total_points} pts)"


class EventAttendanceIntent(models.Model):
    ATTENDING = "yes"
    NOT_ATTENDING = "no"
    UNKNOWN = "unknown"
    STATUS_CHOICES = [
        (ATTENDING, "Will attend"),
        (NOT_ATTENDING, "Will not attend"),
        (UNKNOWN, "Not sure"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_intents",
    )
    quota_period = models.ForeignKey(QuotaPeriod, on_delete=models.CASCADE, related_name="attendance_intents")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=UNKNOWN)

    class Meta:
        unique_together = [("user", "quota_period")]
        verbose_name = "Event Attendance Intent"
        verbose_name_plural = "Event Attendance Intents"

    def __str__(self):
        return f"{self.user} – {self.quota_period}: {self.status}"
