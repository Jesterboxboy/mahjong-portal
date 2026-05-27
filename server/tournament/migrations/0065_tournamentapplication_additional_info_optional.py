from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0064_tournament_application_improvements"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tournamentapplication",
            name="additional_info",
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name="Additional info",
                help_text="More information about tournament",
            ),
        ),
    ]
