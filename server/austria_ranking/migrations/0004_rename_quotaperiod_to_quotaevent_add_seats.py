from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("austria_ranking", "0003_event_attendance_intent"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="QuotaPeriod",
            new_name="QuotaEvent",
        ),
        migrations.AlterModelOptions(
            name="quotaevent",
            options={
                "ordering": ["-end_date"],
                "verbose_name": "Quota Event",
                "verbose_name_plural": "Quota Events",
            },
        ),
        migrations.AddField(
            model_name="quotaevent",
            name="seats_available",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                help_text="If set, the first N confirmed-attending players earn a guaranteed seat (shown with ✓ in the ranking).",
            ),
        ),
    ]
