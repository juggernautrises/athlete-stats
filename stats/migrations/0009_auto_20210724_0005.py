# Generated by Django 3.1.8 on 2021-07-24 00:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0008_mood'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mood',
            old_name='mood_number',
            new_name='number',
        ),
    ]