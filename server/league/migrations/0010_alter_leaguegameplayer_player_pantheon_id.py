# Generated by Django 3.2.10 on 2022-02-06 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0009_auto_20220206_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaguegameplayer',
            name='player_pantheon_id',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]