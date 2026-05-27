from django.db import migrations


class Migration(migrations.Migration):
    """Drop language-specific name columns for Club.

    Club names are language-independent. Club descriptions may differ per
    language and are kept.
    """

    dependencies = [
        ("club", "0010_remove_club_description_ru_remove_club_name_ru_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="club", name="name_de"),
        migrations.RemoveField(model_name="club", name="name_en"),
    ]
