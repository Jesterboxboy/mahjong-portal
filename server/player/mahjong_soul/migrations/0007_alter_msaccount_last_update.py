# Generated by Django 4.2.9 on 2024-03-04 07:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mahjong_soul", "0006_msaccount_last_update"),
    ]

    operations = [
        migrations.AlterField(
            model_name="msaccount",
            name="last_update",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
