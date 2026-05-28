# -*- coding: utf-8 -*-

from datetime import date

from django import forms
from django.contrib import admin, messages
from django.shortcuts import render

from player.models import Player, PlayerQuotaEvent, PlayerTitle
from player.tenhou.models import TenhouNickname
from vereinsmitglieder.models import Mitgliedschaftsbeitrag


def set_yearly_club_fee(modeladmin, request, queryset):
    if request.POST.get("confirmed"):
        try:
            year = int(request.POST.get("fee_year", 0))
        except (ValueError, TypeError):
            modeladmin.message_user(request, "Ungültiges Jahr.", level=messages.ERROR)
            return

        created_count = 0
        for player in queryset:
            _, created = Mitgliedschaftsbeitrag.objects.get_or_create(player=player, year=year)
            if created:
                created_count += 1

        skipped = queryset.count() - created_count
        modeladmin.message_user(
            request,
            f"{created_count} Einträge angelegt, {skipped} bereits vorhanden (Jahr {year}).",
        )
        return

    return render(
        request,
        "admin/player/set_club_fee.html",
        {
            "player_count": queryset.count(),
            "player_pks": list(queryset.values_list("pk", flat=True)),
            "default_year": date.today().year,
        },
    )


set_yearly_club_fee.short_description = "Set Yearly Club Fee status"


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        exclude = []


class TenhouNicknameInline(admin.TabularInline):
    model = TenhouNickname
    extra = 1


class PlayerAdmin(admin.ModelAdmin):
    form = PlayerForm
    inlines = [TenhouNicknameInline]

    prepopulated_fields = {"slug": ["last_name", "first_name"]}

    list_display = ["last_name", "first_name", "city", "pantheon_id"]
    list_filter = ["is_hide", "country"]
    search_fields = ["first_name", "last_name", "ema_id"]
    actions = [set_yearly_club_fee]

    def get_queryset(self, request):
        return Player.objects.all()


class PlayerTitleForm(forms.ModelForm):
    class Meta:
        model = Player
        exclude = ["text"]


class PlayerTitleAdmin(admin.ModelAdmin):
    form = PlayerTitleForm

    search_fields = ["player__last_name", "player__first_name"]
    list_display = ["player", "text", "background_color", "text_color"]
    raw_id_fields = ["player"]


class PlayerQuotaEventAdmin(admin.ModelAdmin):
    search_fields = ["player__first_name", "player__last_name"]
    list_display = ["player", "type", "place", "state", "federation_member"]
    list_filter = ["type", "state"]
    raw_id_fields = ["player"]


admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayerQuotaEvent, PlayerQuotaEventAdmin)
admin.site.register(PlayerTitle, PlayerTitleAdmin)
