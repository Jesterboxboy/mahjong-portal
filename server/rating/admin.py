# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin

from rating.models import ExternalRating, ExternalRatingDelta, Rating, RatingDate


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["name", "slug", "description", "type", "order"]


class ExternalRatingForm(forms.ModelForm):
    class Meta:
        model = ExternalRating
        fields = ["name", "slug", "description", "type", "order", "is_hidden"]


class RatingAdmin(admin.ModelAdmin):
    form = RatingForm
    list_display = ["name", "type", "order"]


class RatingDateAdmin(admin.ModelAdmin):
    list_display = ["date", "rating"]
    list_filter = ["rating"]


class ExternalRatingAdmin(admin.ModelAdmin):
    form = ExternalRatingForm
    list_display = ["name", "order"]


class ExternalRatingDeltaForm(forms.ModelForm):
    class Meta:
        model = ExternalRatingDelta
        exclude = ["player", "date", "rating"]


class ExternalRatingDeltaAdmin(admin.ModelAdmin):
    form = ExternalRatingDeltaForm
    list_display = ["player", "date", "rating"]


admin.site.register(Rating, RatingAdmin)
admin.site.register(RatingDate, RatingDateAdmin)
admin.site.register(ExternalRating, ExternalRatingAdmin)
admin.site.register(ExternalRatingDelta, ExternalRatingDeltaAdmin)
