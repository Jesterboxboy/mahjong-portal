# -*- coding: utf-8 -*-

# Generated by Django 4.2.9 on 2024-02-11 13:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("online", "0024_alter_tournamentgame_log_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournamentplayers",
            name="is_disable",
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
