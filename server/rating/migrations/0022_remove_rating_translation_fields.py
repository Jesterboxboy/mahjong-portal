# -*- coding: utf-8 -*-
"""
Remove modeltranslation DE/EN columns from Rating and ExternalRating.
German (DE) was the default language, so we copy name_de → name and
description_de → description before dropping all language-specific columns.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rating", "0021_remove_externalrating_description_ru_and_more"),
    ]

    operations = [
        # --- Rating ---
        migrations.RunSQL(
            "UPDATE rating_rating SET name = name_de WHERE name_de IS NOT NULL AND name_de != ''",
            migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "UPDATE rating_rating SET description = description_de WHERE description_de IS NOT NULL AND description_de != ''",
            migrations.RunSQL.noop,
        ),
        migrations.RemoveField(model_name="rating", name="name_de"),
        migrations.RemoveField(model_name="rating", name="name_en"),
        migrations.RemoveField(model_name="rating", name="description_de"),
        migrations.RemoveField(model_name="rating", name="description_en"),
        # --- ExternalRating ---
        migrations.RunSQL(
            "UPDATE rating_externalrating SET name = name_de WHERE name_de IS NOT NULL AND name_de != ''",
            migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "UPDATE rating_externalrating SET description = description_de WHERE description_de IS NOT NULL AND description_de != ''",
            migrations.RunSQL.noop,
        ),
        migrations.RemoveField(model_name="externalrating", name="name_de"),
        migrations.RemoveField(model_name="externalrating", name="name_en"),
        migrations.RemoveField(model_name="externalrating", name="description_de"),
        migrations.RemoveField(model_name="externalrating", name="description_en"),
    ]
