# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-26 14:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='timezone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
