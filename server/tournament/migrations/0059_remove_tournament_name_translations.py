from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0058_remove_tournament_name_ru_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tournament",
            name="name_de",
        ),
        migrations.RemoveField(
            model_name="tournament",
            name="name_en",
        ),
    ]
