# -*- coding: utf-8 -*-

from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe

from player.models import Player


class AddPlayerForm(forms.ModelForm):
    last_name = forms.CharField(label="Nachname")
    first_name = forms.CharField(label="Vorname")

    class Meta:
        model = Player
        fields = ["last_name", "first_name", "city"]

    def __init__(self, *args, **kwargs):
        super(AddPlayerForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(AddPlayerForm, self).clean()

        first_name = data.get("first_name")
        last_name = data.get("last_name")

        if first_name and last_name:
            first_name = first_name.title()
            last_name = last_name.title()

            try:
                player = Player.objects.get(first_name=first_name, last_name=last_name)
                if player.ema_id:
                    raise forms.ValidationError(
                        "Spieler mit diesem Namen existiert bereits und hat EMA-ID {}.".format(player.ema_id)
                    )
                else:
                    message = "Spieler mit diesem Namen existiert bereits."
                    if player.city:
                        message += " Aus {}.".format(player.city.name)

                    message += " {}.".format(player.country.name)

                    link = "<a href={}>Ja, Los!</a>".format(reverse("assign_ema_id", kwargs={"player_id": player.id}))
                    message += " EMA-ID hinzufügen? {}".format(link)

                    raise forms.ValidationError(mark_safe(message))

            except Player.MultipleObjectsReturned:
                raise forms.ValidationError(
                    "Mehrere Spieler mit diesem Namen gefunden. Bitte Administrator kontaktieren."
                ) from None
            except Player.DoesNotExist:
                pass

        return data
