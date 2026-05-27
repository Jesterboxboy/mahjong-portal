# Generated migration

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0061_add_email_to_registration_make_phone_optional"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournament",
            name="venue_address",
            field=models.TextField(blank=True, null=True, verbose_name="Venue & address"),
        ),
        migrations.AddField(
            model_name="tournament",
            name="schedule",
            field=models.TextField(blank=True, null=True, verbose_name="Schedule / Itinerary"),
        ),
        migrations.AddField(
            model_name="tournament",
            name="lunch_options",
            field=models.TextField(blank=True, null=True, verbose_name="Lunch options"),
        ),
        migrations.AddField(
            model_name="tournament",
            name="contact_info",
            field=models.TextField(blank=True, null=True, verbose_name="Contact information"),
        ),
        migrations.AddField(
            model_name="tournament",
            name="gdpr_document",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="tournament/gdpr/",
                verbose_name="GDPR document (PDF)",
            ),
        ),
        migrations.AddField(
            model_name="tournamentregistration",
            name="registration_country",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="Country"),
        ),
        migrations.AddField(
            model_name="onlinetournamentregistration",
            name="registration_country",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="Country"),
        ),
    ]
