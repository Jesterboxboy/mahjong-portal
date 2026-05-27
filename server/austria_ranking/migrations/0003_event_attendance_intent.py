import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("austria_ranking", "0002_add_ema_tournament_url"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EventAttendanceIntent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[("yes", "Will attend"), ("no", "Will not attend"), ("unknown", "Not sure")],
                        default="unknown",
                        max_length=10,
                    ),
                ),
                (
                    "quota_period",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attendance_intents",
                        to="austria_ranking.quotaperiod",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attendance_intents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Event Attendance Intent",
                "verbose_name_plural": "Event Attendance Intents",
            },
        ),
        migrations.AlterUniqueTogether(
            name="eventattendanceintent",
            unique_together={("user", "quota_period")},
        ),
    ]
