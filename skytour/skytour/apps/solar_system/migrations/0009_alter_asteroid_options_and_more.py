# Generated by Django 4.0.1 on 2022-01-10 03:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solar_system', '0008_asteroid'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asteroid',
            options={'ordering': ['number']},
        ),
        migrations.RemoveField(
            model_name='asteroid',
            name='arg_perihelion',
        ),
        migrations.RemoveField(
            model_name='asteroid',
            name='daily_motion',
        ),
        migrations.RemoveField(
            model_name='asteroid',
            name='eccentricity',
        ),
        migrations.RemoveField(
            model_name='asteroid',
            name='epoch',
        ),
        migrations.RemoveField(
            model_name='asteroid',
            name='inclination',
        ),
        migrations.RemoveField(
            model_name='asteroid',
            name='long_asc_node',
        ),
        migrations.RemoveField(
            model_name='asteroid',
            name='mean_anomaly',
        ),
        migrations.RemoveField(
            model_name='asteroid',
            name='semi_major_axis',
        ),
    ]