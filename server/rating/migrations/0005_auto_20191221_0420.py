# -*- coding: utf-8 -*-

# Generated by Django 2.2.6 on 2019-12-21 04:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rating', '0004_tournamentcoefficients_previous_age'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ratingdelta',
            name='is_last',
        ),
        migrations.RemoveField(
            model_name='ratingresult',
            name='is_last',
        ),
        migrations.CreateModel(
            name='RatingDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(db_index=True)),
                ('is_future', models.BooleanField(default=False)),
                ('rating', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rating.Rating')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
