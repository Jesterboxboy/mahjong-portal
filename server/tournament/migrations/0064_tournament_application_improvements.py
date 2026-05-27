from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0063_info_fields_translations"),
    ]

    operations = [
        # tournament_type: PositiveSmallIntegerField → CharField with ema/other/online
        migrations.RemoveField(
            model_name="tournamentapplication",
            name="tournament_type",
        ),
        migrations.AddField(
            model_name="tournamentapplication",
            name="tournament_type",
            field=models.CharField(
                choices=[["ema", "EMA"], ["other", "Other"], ["online", "Online"]],
                default="ema",
                max_length=10,
                verbose_name="Tournament type",
            ),
        ),
        # Add country field
        migrations.AddField(
            model_name="tournamentapplication",
            name="country",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="Country"),
        ),
        # Bilingual info fields
        migrations.AddField(
            model_name="tournamentapplication",
            name="venue_address_de",
            field=models.TextField(blank=True, null=True, verbose_name="Venue & address (DE)"),
        ),
        migrations.AddField(
            model_name="tournamentapplication",
            name="venue_address_en",
            field=models.TextField(blank=True, null=True, verbose_name="Venue & address (EN)"),
        ),
        migrations.AddField(
            model_name="tournamentapplication",
            name="schedule_de",
            field=models.TextField(blank=True, null=True, verbose_name="Schedule / Itinerary (DE)"),
        ),
        migrations.AddField(
            model_name="tournamentapplication",
            name="schedule_en",
            field=models.TextField(blank=True, null=True, verbose_name="Schedule / Itinerary (EN)"),
        ),
        migrations.AddField(
            model_name="tournamentapplication",
            name="lunch_options_de",
            field=models.TextField(blank=True, null=True, verbose_name="Lunch options (DE)"),
        ),
        migrations.AddField(
            model_name="tournamentapplication",
            name="lunch_options_en",
            field=models.TextField(blank=True, null=True, verbose_name="Lunch options (EN)"),
        ),
        migrations.AddField(
            model_name="tournamentapplication",
            name="contact_info_de",
            field=models.TextField(blank=True, null=True, verbose_name="Contact information (DE)"),
        ),
        migrations.AddField(
            model_name="tournamentapplication",
            name="contact_info_en",
            field=models.TextField(blank=True, null=True, verbose_name="Contact information (EN)"),
        ),
        # organizer_phone: make optional
        migrations.AlterField(
            model_name="tournamentapplication",
            name="organizer_phone",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="Organizer phone"),
        ),
        # organizer_additional_contact → organizer_email
        migrations.RenameField(
            model_name="tournamentapplication",
            old_name="organizer_additional_contact",
            new_name="organizer_email",
        ),
        migrations.AlterField(
            model_name="tournamentapplication",
            name="organizer_email",
            field=models.EmailField(max_length=255, null=True, verbose_name="Organizer email"),
        ),
        # referee_name: make optional
        migrations.AlterField(
            model_name="tournamentapplication",
            name="referee_name",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="Referee name"),
        ),
        # referee_phone: make optional
        migrations.AlterField(
            model_name="tournamentapplication",
            name="referee_phone",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="Referee phone"),
        ),
        # referee_additional_contact → referee_email
        migrations.RenameField(
            model_name="tournamentapplication",
            old_name="referee_additional_contact",
            new_name="referee_email",
        ),
        migrations.AlterField(
            model_name="tournamentapplication",
            name="referee_email",
            field=models.EmailField(blank=True, max_length=255, null=True, verbose_name="Referee email"),
        ),
    ]
