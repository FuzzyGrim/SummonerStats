# Generated by Django 4.0.1 on 2022-07-08 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_match_player_json'),
    ]

    operations = [
        migrations.RenameField(
            model_name='match',
            old_name='summary_json',
            new_name='match_json',
        ),
        migrations.RenameField(
            model_name='match',
            old_name='player_json',
            new_name='summoner_json',
        ),
    ]
