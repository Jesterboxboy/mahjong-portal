# -*- coding: utf-8 -*-

from modeltranslation.translator import TranslationOptions, translator

from austria_ranking.models import QualificationModeInfo, QuotaEvent


class QuotaEventTranslationOptions(TranslationOptions):
    fields = ["event_info"]


class QualificationModeInfoTranslationOptions(TranslationOptions):
    fields = ["info_text"]


translator.register(QuotaEvent, QuotaEventTranslationOptions)
translator.register(QualificationModeInfo, QualificationModeInfoTranslationOptions)
