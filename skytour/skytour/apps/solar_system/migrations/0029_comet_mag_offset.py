# Generated by Django 4.0.4 on 2022-06-30 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar_system', '0028_alter_asteroidobservation_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comet',
            name='mag_offset',
            field=models.FloatField(default=0.0, verbose_name='Mag Offset'),
        ),
    ]
