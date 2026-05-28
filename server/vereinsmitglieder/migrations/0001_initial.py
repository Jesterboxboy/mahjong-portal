# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("player", "0020_remove_player_name_translations"),
    ]

    operations = [
        migrations.CreateModel(
            name="Mitgliedschaftsbeitrag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("year", models.PositiveIntegerField(verbose_name="Jahr")),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="membership_fees",
                        to="player.player",
                        verbose_name="Spieler",
                    ),
                ),
            ],
            options={
                "verbose_name": "Mitgliedschaftsbeitrag",
                "verbose_name_plural": "Mitgliedschaftsbeitr\u00e4ge",
                "ordering": ["-year", "player__last_name", "player__first_name"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="mitgliedschaftsbeitrag",
            unique_together={("year", "player")},
        ),
    ]
