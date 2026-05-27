# -*- coding: utf-8 -*-

from modeltranslation.translator import TranslationOptions, translator

from tournament.models import Tournament


class TournamentTranslationOptions(TranslationOptions):
    fields = ["registration_description", "results_description", "venue_address", "schedule", "lunch_options", "contact_info"]


translator.register(Tournament, TournamentTranslationOptions)
