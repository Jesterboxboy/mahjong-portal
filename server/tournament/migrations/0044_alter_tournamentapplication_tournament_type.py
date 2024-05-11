# Generated by Django 4.2.9 on 2024-05-11 08:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tournament", "0043_tournament_is_apply_in_rating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tournamentapplication",
            name="tournament_type",
            field=models.PositiveSmallIntegerField(
                choices=[[0, "CRR"], [1, "RR"], [2, "EMA"], [3, "OTHER"]], default=0, verbose_name="Tournament type"
            ),
        ),
    ]
