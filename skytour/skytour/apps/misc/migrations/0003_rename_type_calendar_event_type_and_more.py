# Generated by Django 4.0 on 2022-01-03 22:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('misc', '0002_alter_stateregion_options_alter_timezone_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='calendar',
            old_name='type',
            new_name='event_type',
        ),
        migrations.RenameField(
            model_name='calendar',
            old_name='event',
            new_name='title',
        ),
    ]