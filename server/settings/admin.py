# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin

from settings.models import City, Country


class CountryAdmin(admin.ModelAdmin):
    list_display = ["name"]


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        exclude = []


class CityAdmin(admin.ModelAdmin):
    form = CityForm
    list_display = ["name"]
    search_fields = ["name"]

    prepopulated_fields = {"slug": ["name"]}


admin.site.register(Country, CountryAdmin)
admin.site.register(City, CityAdmin)
