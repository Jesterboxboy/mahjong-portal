# -*- coding: utf-8 -*-

# Generated by Django 3.2.10 on 2022-02-06 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0006_leaguegame_leaguegameplayer_leaguesession'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='leaguesession',
            options={'ordering': ['number']},
        ),
        migrations.AddField(
            model_name='leaguesession',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[[0, 'Planned'], [1, 'Finished']], default=0),
        ),
    ]
