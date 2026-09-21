# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
from django.utils.html import format_html

from pantheon_api.api_calls.user import get_current_pantheon_user_data, login_through_pantheon
from settings.models import City, Country, FreyConnector


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


class FreyConnectorForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="Used once to fetch a fresh auth token from Frey; never stored. "
        "Enter it again after the account's password changes.",
    )

    class Meta:
        model = FreyConnector
        fields = ["email", "password", "person_id", "auth_token"]

    def clean(self):
        data = super().clean()
        password = data.get("password")
        if not password:
            return data
        if not data.get("email"):
            raise forms.ValidationError("Email is required to log in to Frey.")
        try:
            response = login_through_pantheon(data["email"].strip(), password)
        except Exception as e:  # noqa: BLE001
            raise forms.ValidationError(f"Frey login failed: {e}") from e
        data["person_id"] = response.person_id
        data["auth_token"] = response.auth_token
        return data


class FreyConnectorAdmin(admin.ModelAdmin):
    form = FreyConnectorForm
    list_display = ["__str__", "email", "person_id", "connection_status"]
    readonly_fields = ["connection_status"]

    def has_add_permission(self, request):
        return not FreyConnector.objects.exists()

    @admin.display(description="Connection status")
    def connection_status(self, obj):
        # Live check against the credentials actually in use (this row, or the env fallback).
        person_id, token = FreyConnector.credentials()
        if not (person_id and token):
            return format_html('<span style="color:#b00">{}</span>', "Not configured")
        try:
            me = get_current_pantheon_user_data(person_id, token)
        except Exception as e:  # noqa: BLE001
            return format_html('<span style="color:#b00">✗ {}</span>', e)
        return format_html('<span style="color:#080">✓ Connected as {} (id {})</span>', me["email"], me["person_id"])


admin.site.register(Country, CountryAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(FreyConnector, FreyConnectorAdmin)
