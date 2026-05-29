# -*- coding: utf-8 -*-
# Generated manually for Improvement 16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("austria_ranking", "0004_rename_quotaperiod_to_quotaevent_add_seats"),
    ]

    operations = [
        # Add event_info fields (base + translations) to QuotaEvent
        migrations.AddField(
            model_name="quotaevent",
            name="event_info",
            field=models.TextField(blank=True, null=True, verbose_name="Eventinformation"),
        ),
        migrations.AddField(
            model_name="quotaevent",
            name="event_info_de",
            field=models.TextField(blank=True, null=True, verbose_name="Eventinformation [de]"),
        ),
        migrations.AddField(
            model_name="quotaevent",
            name="event_info_en",
            field=models.TextField(blank=True, null=True, verbose_name="Eventinformation [en]"),
        ),
        # Create QualificationModeInfo singleton model
        migrations.CreateModel(
            name="QualificationModeInfo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "info_text",
                    models.TextField(
                        blank=True, default="", verbose_name="Informationen zum Qualifikationsmodus"
                    ),
                ),
                (
                    "info_text_de",
                    models.TextField(
                        blank=True, null=True, verbose_name="Informationen zum Qualifikationsmodus [de]"
                    ),
                ),
                (
                    "info_text_en",
                    models.TextField(
                        blank=True, null=True, verbose_name="Informationen zum Qualifikationsmodus [en]"
                    ),
                ),
            ],
            options={
                "verbose_name": "Qualifikationsmodus Info",
                "verbose_name_plural": "Qualifikationsmodus Info",
            },
        ),
    ]
