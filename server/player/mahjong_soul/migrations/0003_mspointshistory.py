# -*- coding: utf-8 -*-

# Generated by Django 2.2.6 on 2019-10-26 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mahjong_soul', '0002_auto_20191024_1317'),
    ]

    operations = [
        migrations.CreateModel(
            name='MSPointsHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank_index', models.PositiveSmallIntegerField()),
                ('rank', models.PositiveSmallIntegerField()),
                ('points', models.PositiveSmallIntegerField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('stat_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mahjong_soul.MSAccountStatistic')),
            ],
        ),
    ]
