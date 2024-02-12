# -*- coding: utf-8 -*-

# Generated by Django 3.2.10 on 2022-02-06 14:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0005_auto_20220203_0245'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeagueSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField()),
                ('start_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='LeagueGamePlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveSmallIntegerField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='players', to='league.leaguesession')),
            ],
        ),
        migrations.CreateModel(
            name='LeagueGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[[0, 'New'], [1, 'Started'], [2, 'Finished']], default=0)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='games', to='league.leaguesession')),
            ],
        ),
    ]
