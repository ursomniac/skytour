# Generated by Django 4.0.1 on 2022-02-03 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solar_system', '0015_alter_asteroidobservation_seeing_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asteroidobservation',
            name='seeing',
        ),
        migrations.RemoveField(
            model_name='asteroidobservation',
            name='sqm',
        ),
        migrations.RemoveField(
            model_name='cometobservation',
            name='seeing',
        ),
        migrations.RemoveField(
            model_name='cometobservation',
            name='sqm',
        ),
        migrations.RemoveField(
            model_name='planetobservation',
            name='seeing',
        ),
        migrations.RemoveField(
            model_name='planetobservation',
            name='sqm',
        ),
    ]
