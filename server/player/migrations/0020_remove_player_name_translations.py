from django.db import migrations


class Migration(migrations.Migration):
    """Drop language-specific name/first_name/last_name columns for Player.

    Player names are written the same way regardless of site language.
    """

    dependencies = [
        ("player", "0019_remove_player_first_name_ru_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="player", name="first_name_de"),
        migrations.RemoveField(model_name="player", name="first_name_en"),
        migrations.RemoveField(model_name="player", name="last_name_de"),
        migrations.RemoveField(model_name="player", name="last_name_en"),
    ]
