# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-18 11:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='slug',
            field=models.SlugField(max_length=255, unique=True),
        ),
    ]