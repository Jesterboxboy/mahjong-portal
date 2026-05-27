from django.db import migrations


class Migration(migrations.Migration):
    """Drop the language-specific name columns for City and Country.

    These were created by django-modeltranslation but are no longer needed:
    names like "Wien" or "Austria" are the same in every language.
    """

    dependencies = [
        ("settings", "0005_remove_city_name_ru_remove_country_name_ru_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="city", name="name_de"),
        migrations.RemoveField(model_name="city", name="name_en"),
        migrations.RemoveField(model_name="country", name="name_de"),
        migrations.RemoveField(model_name="country", name="name_en"),
    ]
