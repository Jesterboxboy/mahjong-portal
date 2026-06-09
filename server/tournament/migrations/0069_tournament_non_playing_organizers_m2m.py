from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("player", "0020_remove_player_name_translations"),
        ("tournament", "0068_add_non_playing_organizer"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tournament",
            name="non_playing_organizer",
        ),
        migrations.AddField(
            model_name="tournament",
            name="non_playing_organizers",
            field=models.ManyToManyField(
                blank=True,
                help_text="Players who organize this tournament but do not compete. Each receives a share of their average AT points for this quota period.",
                related_name="organized_tournaments",
                to="player.player",
                verbose_name="Non-playing organizers",
            ),
        ),
    ]
