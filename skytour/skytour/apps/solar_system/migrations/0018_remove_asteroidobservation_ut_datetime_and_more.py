# Generated by Django 4.0.2 on 2022-02-09 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar_system', '0017_remove_asteroidobservation_ut_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asteroidobservation',
            name='ut_datetime',
        ),
        migrations.RemoveField(
            model_name='cometobservation',
            name='ut_datetime',
        ),
        migrations.RemoveField(
            model_name='planetobservation',
            name='ut_datetime',
        ),
        migrations.AddField(
            model_name='asteroidobservation',
            name='ut_date',
            field=models.DateField(blank=True, help_text='UT Date', null=True, verbose_name='Date of Obs'),
        ),
        migrations.AddField(
            model_name='asteroidobservation',
            name='ut_time',
            field=models.TimeField(blank=True, help_text='UT Time', null=True, verbose_name='Time of Obs'),
        ),
        migrations.AddField(
            model_name='cometobservation',
            name='ut_date',
            field=models.DateField(blank=True, help_text='UT Date', null=True, verbose_name='Date of Obs'),
        ),
        migrations.AddField(
            model_name='cometobservation',
            name='ut_time',
            field=models.TimeField(blank=True, help_text='UT Time', null=True, verbose_name='Time of Obs'),
        ),
        migrations.AddField(
            model_name='planetobservation',
            name='ut_date',
            field=models.DateField(blank=True, help_text='UT Date', null=True, verbose_name='Date of Obs'),
        ),
        migrations.AddField(
            model_name='planetobservation',
            name='ut_time',
            field=models.TimeField(blank=True, help_text='UT Time', null=True, verbose_name='Time of Obs'),
        ),
    ]
