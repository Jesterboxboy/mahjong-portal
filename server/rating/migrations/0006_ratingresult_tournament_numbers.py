# -*- coding: utf-8 -*-

# Generated by Django 2.2.6 on 2019-12-30 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rating', '0005_auto_20191221_0420'),
    ]

    operations = [
        migrations.AddField(
            model_name='ratingresult',
            name='tournament_numbers',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
