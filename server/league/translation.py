# -*- coding: utf-8 -*-

from modeltranslation.translator import TranslationOptions, translator

from player.models import PlayerTitle


# Player first/last names are language-independent — no translation needed.


class PlayerTitleOptions(TranslationOptions):
    fields = ["text"]


translator.register(PlayerTitle, PlayerTitleOptions)
