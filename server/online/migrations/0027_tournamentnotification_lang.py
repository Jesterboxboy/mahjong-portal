# Generated by Django 4.2.9 on 2024-06-08 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("online", "0026_alter_tournamentplayers_unique_together"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournamentnotification",
            name="lang",
            field=models.CharField(choices=[["RU", "RU"], ["EN", "EN"]], default="RU", max_length=2),
        ),
    ]
