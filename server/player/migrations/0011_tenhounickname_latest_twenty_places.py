# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-06-28 15:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0010_collectedyakuman'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenhounickname',
            name='latest_twenty_places',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]