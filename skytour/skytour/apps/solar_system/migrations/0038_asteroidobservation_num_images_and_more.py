# Generated by Django 4.0.4 on 2023-07-23 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar_system', '0037_asteroidobservation_imaging_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='asteroidobservation',
            name='num_images',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cometobservation',
            name='num_images',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='moonobservation',
            name='num_images',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='planetobservation',
            name='num_images',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
