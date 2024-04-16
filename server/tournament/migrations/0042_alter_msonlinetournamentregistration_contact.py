# -*- coding: utf-8 -*-

# Generated by Django 4.2.9 on 2024-01-30 22:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tournament", "0041_alter_msonlinetournamentregistration_ms_account_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="msonlinetournamentregistration",
            name="contact",
            field=models.CharField(
                blank=True,
                help_text="It will be visible only to the administrator",
                max_length=255,
                null=True,
                verbose_name="Your contact (email, phone, etc.)",
            ),
        ),
    ]
