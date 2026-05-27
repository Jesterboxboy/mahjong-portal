from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0062_improvement2_info_fields"),
    ]

    operations = [
        # venue_address translations
        migrations.AddField(
            model_name="tournament",
            name="venue_address_de",
            field=models.TextField(blank=True, default="", null=True, verbose_name="Venue & address"),
        ),
        migrations.AddField(
            model_name="tournament",
            name="venue_address_en",
            field=models.TextField(blank=True, default="", null=True, verbose_name="Venue & address"),
        ),
        # schedule translations
        migrations.AddField(
            model_name="tournament",
            name="schedule_de",
            field=models.TextField(blank=True, default="", null=True, verbose_name="Schedule / Itinerary"),
        ),
        migrations.AddField(
            model_name="tournament",
            name="schedule_en",
            field=models.TextField(blank=True, default="", null=True, verbose_name="Schedule / Itinerary"),
        ),
        # lunch_options translations
        migrations.AddField(
            model_name="tournament",
            name="lunch_options_de",
            field=models.TextField(blank=True, default="", null=True, verbose_name="Lunch options"),
        ),
        migrations.AddField(
            model_name="tournament",
            name="lunch_options_en",
            field=models.TextField(blank=True, default="", null=True, verbose_name="Lunch options"),
        ),
        # contact_info translations
        migrations.AddField(
            model_name="tournament",
            name="contact_info_de",
            field=models.TextField(blank=True, default="", null=True, verbose_name="Contact information"),
        ),
        migrations.AddField(
            model_name="tournament",
            name="contact_info_en",
            field=models.TextField(blank=True, default="", null=True, verbose_name="Contact information"),
        ),
    ]
