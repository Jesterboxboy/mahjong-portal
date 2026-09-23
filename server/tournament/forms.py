# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import gettext_lazy as _

from settings.models import Country
from tournament.models import (
    MsOnlineTournamentRegistration,
    OnlineTournamentRegistration,
    TournamentApplication,
    TournamentRegistration,
)


def _use_country_dropdown(form):
    """Replace the free-text country input with the Country table as a dropdown.

    Values outside the table are rejected — that is the point: the field used to collect
    "Ausitra" and "Osterreich" for the same country. Seed the table with
    `manage.py seed_countries`.
    """
    field = form.fields["registration_country"]
    form.fields["registration_country"] = forms.ChoiceField(
        choices=[("", "---------")] + list(Country.objects.values_list("name", "name")),
        label=field.label,
        required=field.required,
    )


class TournamentRegistrationForm(forms.ModelForm):
    allow_to_save_data = forms.BooleanField(required=True)
    required_css_class = "required-field"

    class Meta:
        model = TournamentRegistration
        fields = [
            "last_name",
            "first_name",
            "registration_country",
            "city",
            "email",
            "phone",
            "ema_id",
            "notes",
            "allow_to_save_data",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tournament = kwargs.get("initial", {}).get("tournament")

        self.fields["allow_to_save_data"].label = _("I allow to store my personal data")
        _use_country_dropdown(self)
        if tournament.display_notes:
            self.fields["notes"].widget = forms.Textarea(attrs={"rows": 2})
            if tournament.is_command:
                self.fields["notes"].label = _("Team name")
        else:
            del self.fields["notes"]


class OnlineTournamentRegistrationForm(forms.ModelForm):
    allow_to_save_data = forms.BooleanField(required=True)
    required_css_class = "required-field"

    class Meta:
        model = OnlineTournamentRegistration
        fields = [
            "last_name",
            "first_name",
            "registration_country",
            "city",
            "tenhou_nickname",
            "contact",
            "notes",
            "allow_to_save_data",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tournament = kwargs.get("initial", {}).get("tournament")

        self.fields["allow_to_save_data"].label = _("I allow to store my personal data")
        _use_country_dropdown(self)

        if tournament.display_notes:
            self.fields["notes"].widget = forms.Textarea(attrs={"rows": 2})
        else:
            del self.fields["notes"]

        if tournament.is_majsoul_tournament:
            self.fields["tenhou_nickname"].label = _("Majsoul nickname")


class OnlineTournamentPantheonRegistrationForm(forms.ModelForm):
    allow_to_save_data = forms.BooleanField(required=True)
    required_css_class = "required-field"

    class Meta:
        model = OnlineTournamentRegistration
        fields = ["notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tournament = kwargs.get("initial", {}).get("tournament")

        if tournament.display_notes:
            self.fields["notes"].widget = forms.Textarea(attrs={"rows": 2})
            if tournament.is_command:
                self.fields["notes"].label = _("Team name")
        else:
            del self.fields["notes"]

        del self.fields["allow_to_save_data"]


class MajsoulOnlineTournamentPantheonRegistrationForm(forms.ModelForm):
    allow_to_save_data = forms.BooleanField(required=False)

    class Meta:
        model = MsOnlineTournamentRegistration
        fields = ["ms_friend_id", "ms_nickname", "notes", "allow_to_save_data"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tournament = kwargs.get("initial", {}).get("tournament")

        if tournament.is_majsoul_tournament:
            self.fields["ms_friend_id"].label = _("Majsoul friend id")
            self.fields["ms_nickname"].label = _("Majsoul nickname")

        if tournament.display_notes:
            self.fields["notes"].widget = forms.Textarea(attrs={"rows": 2})
            if tournament.is_command:
                self.fields["notes"].label = _("Team name")
        else:
            del self.fields["notes"]

        self.fields["allow_to_save_data"].label = _(
            "I allow to add my majsoul account at mahjong portal for statistics (optional)"
        )


class TournamentApplicationForm(forms.ModelForm):
    allow_to_save_data = forms.BooleanField(required=True)
    is_admin_myself = forms.BooleanField(required=False)
    required_css_class = "required-field"

    class Meta:
        model = TournamentApplication
        exclude = ["tournament_admin_user"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["allow_to_save_data"].label = _("I allow to store my personal data")
        self.fields["is_admin_myself"].label = _(
            "I am the organiser, I need to grant access to manage the tournament on portal"
        )
