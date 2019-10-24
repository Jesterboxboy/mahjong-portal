# Generated by Django 2.2.6 on 2019-10-24 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mahjong_soul', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='msaccountstatistic',
            old_name='type',
            new_name='game_type',
        ),
        migrations.RenameField(
            model_name='msaccountstatistic',
            old_name='average_place',
            new_name='hanchan_average_place',
        ),
        migrations.RenameField(
            model_name='msaccountstatistic',
            old_name='first_place',
            new_name='hanchan_first_place',
        ),
        migrations.RenameField(
            model_name='msaccountstatistic',
            old_name='fourth_place',
            new_name='hanchan_fourth_place',
        ),
        migrations.RenameField(
            model_name='msaccountstatistic',
            old_name='second_place',
            new_name='hanchan_second_place',
        ),
        migrations.RenameField(
            model_name='msaccountstatistic',
            old_name='third_place',
            new_name='hanchan_third_place',
        ),
        migrations.RemoveField(
            model_name='msaccountstatistic',
            name='games',
        ),
        migrations.AddField(
            model_name='msaccountstatistic',
            name='hanchan_games',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='msaccountstatistic',
            name='tonpusen_average_place',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='msaccountstatistic',
            name='tonpusen_first_place',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='msaccountstatistic',
            name='tonpusen_fourth_place',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='msaccountstatistic',
            name='tonpusen_games',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='msaccountstatistic',
            name='tonpusen_second_place',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='msaccountstatistic',
            name='tonpusen_third_place',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
