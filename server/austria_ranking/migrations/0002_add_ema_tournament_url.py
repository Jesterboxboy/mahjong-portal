from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("austria_ranking", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ematournamentresult",
            name="ema_tournament_url",
            field=models.URLField(blank=True, default=""),
        ),
    ]
