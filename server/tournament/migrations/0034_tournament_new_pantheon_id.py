# Generated by Django 3.2.18 on 2023-03-15 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0033_rename_pantheon_id_tournament_old_pantheon_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='new_pantheon_id',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
