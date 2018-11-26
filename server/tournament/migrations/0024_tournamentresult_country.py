# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-11-26 02:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0003_delete_tournamenttype'),
        ('tournament', '0023_auto_20180829_1022'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournamentresult',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='settings.Country'),
        ),
    ]