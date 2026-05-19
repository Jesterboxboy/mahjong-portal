# -*- coding: utf-8 -*-

from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe

from player.models import Player


class AddPlayerForm(forms.ModelForm):
    last_name_de = forms.CharField(label="Nachname (auf Deutsch)")
    first_name_de = forms.CharField(label="Vorname (auf Deutsch)")
    last_name_en = forms.CharField(label="Nachname (auf Englisch)")
    first_name_en = forms.CharField(label="Vorname (auf Englisch)")

    class Meta:
        model = Player
        fields = ["last_name_de", "first_name_de", "last_name_en", "first_name_en", "city"]

    def __init__(self, *args, **kwargs):
        super(AddPlayerForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(AddPlayerForm, self).clean()

        first_name_de = data.get("first_name_de")
        last_name_de = data.get("last_name_de")

        if first_name_de and last_name_de:
            first_name_de = first_name_de.title()
            last_name_de = last_name_de.title()

            try:
                player = Player.objects.get(first_name_de=first_name_de, last_name_de=last_name_de)
                if player.ema_id:
                    raise forms.ValidationError(
                        "Игрок с таким именем уже существует и у него есть ema id {}.".format(player.ema_id)
                    )
                else:
                    message = "Игрок с таким именем уже существует."
                    if player.city:
                        message += " Из города {}.".format(player.city.name)

                    message += " {}.".format(player.country.name)

                    link = "<a href={}>Да, давай!</a>".format(reverse("assign_ema_id", kwargs={"player_id": player.id}))
                    message += " Добавить ему EMA id? {}".format(link)

                    raise forms.ValidationError(mark_safe(message))

            except Player.MultipleObjectsReturned:
                raise forms.ValidationError(
                    "Игроков с таким именем уже несколько. Обратитесь к администратору."
                ) from None
            except Player.DoesNotExist:
                pass

        return data
