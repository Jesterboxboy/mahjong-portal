# -*- coding: utf-8 -*-

# Generated by Django 4.2.2 on 2024-01-06 20:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("online", "0023_alter_tournamentplayers_ms_account_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tournamentgame",
            name="log_id",
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
    ]
