# Generated by Django 4.0.1 on 2022-02-01 17:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('solar_system', '0012_comet'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanetObservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ut_date', models.DateField(help_text='UT Date', verbose_name='Date of Obs')),
                ('ut_time', models.TimeField(help_text='UT Time', verbose_name='Time of Obs')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='observations', to='solar_system.planet')),
            ],
            options={
                'verbose_name': 'Observation',
                'verbose_name_plural': 'Observations',
            },
        ),
        migrations.CreateModel(
            name='CometObservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ut_date', models.DateField(help_text='UT Date', verbose_name='Date of Obs')),
                ('ut_time', models.TimeField(help_text='UT Time', verbose_name='Time of Obs')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='observations', to='solar_system.comet')),
            ],
            options={
                'verbose_name': 'Observation',
                'verbose_name_plural': 'Observations',
            },
        ),
        migrations.CreateModel(
            name='AsteroidObservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ut_date', models.DateField(help_text='UT Date', verbose_name='Date of Obs')),
                ('ut_time', models.TimeField(help_text='UT Time', verbose_name='Time of Obs')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='observations', to='solar_system.asteroid')),
            ],
            options={
                'verbose_name': 'Observation',
                'verbose_name_plural': 'Observations',
            },
        ),
    ]
