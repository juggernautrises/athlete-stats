# Generated by Django 3.1.6 on 2021-02-06 04:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StravaTokens',
            new_name='StravaToken',
        ),
    ]
