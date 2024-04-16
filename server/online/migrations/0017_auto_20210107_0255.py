# -*- coding: utf-8 -*-

# Generated by Django 3.0.7 on 2021-01-07 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online', '0016_tournamentplayers_is_replacement'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournamentgame',
            name='game_index',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='tournamentnotification',
            name='notification_type',
            field=models.CharField(choices=[['game_started', 'game_started'], ['game_failed', 'game_failed'], ['game_failed_no_members', 'game_failed_no_members'], ['game_ended', 'game_ended'], ['confirmation_started', 'confirmation_started'], ['confirmation_ended', 'confirmation_ended'], ['games_prepared', 'games_prepared'], ['round_finished', 'round_finished'], ['tournament_finished', 'tournament_finished'], ['game_pre_ended', 'game_pre_ended'], ['game_penalty', 'game_penalty']], max_length=300),
        ),
    ]
