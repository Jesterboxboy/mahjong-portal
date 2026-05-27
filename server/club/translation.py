# -*- coding: utf-8 -*-

from modeltranslation.translator import TranslationOptions, translator

from club.models import Club


# Club name is language-independent. Descriptions can differ per language.
class ClubTranslationOptions(TranslationOptions):
    fields = ["description"]


translator.register(Club, ClubTranslationOptions)
