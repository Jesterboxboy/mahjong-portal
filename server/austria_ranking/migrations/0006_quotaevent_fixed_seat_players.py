# -*- coding: utf-8 -*-
# Generated manually for Improvement 19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("austria_ranking", "0005_improvement16_qualification_mode_info"),
        ("player", "0020_remove_player_name_translations"),
    ]

    operations = [
        migrations.AddField(
            model_name="quotaevent",
            name="fixed_seat_players",
            field=models.ManyToManyField(
                blank=True,
                help_text="Players with a guaranteed seat regardless of ranking. Shown with 👑 (unconfirmed) or ✓ (confirmed attendance).",
                related_name="fixed_quota_events",
                to="player.player",
                verbose_name="Fixed seat players",
            ),
        ),
    ]
