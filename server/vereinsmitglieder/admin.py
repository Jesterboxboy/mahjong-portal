# -*- coding: utf-8 -*-

from django.contrib import admin

from vereinsmitglieder.models import Mitgliedschaftsbeitrag


@admin.register(Mitgliedschaftsbeitrag)
class MitgliedschaftsbeitragAdmin(admin.ModelAdmin):
    list_display = ["year", "player_last_name", "player_first_name"]
    list_filter = ["year"]
    raw_id_fields = ["player"]
    search_fields = ["player__last_name", "player__first_name"]
    ordering = ["-year", "player__last_name", "player__first_name"]

    def player_last_name(self, obj):
        return obj.player.last_name

    player_last_name.short_description = "Nachname"
    player_last_name.admin_order_field = "player__last_name"

    def player_first_name(self, obj):
        return obj.player.first_name

    player_first_name.short_description = "Vorname"
    player_first_name.admin_order_field = "player__first_name"
