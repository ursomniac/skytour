# Generated by Django 4.0.1 on 2022-01-12 21:04

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('observe', '0017_remove_observinglocation_x_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObservingSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('utdt_start', models.DateTimeField(default=datetime.datetime.utcnow, verbose_name='UTDT Start')),
                ('dec_limit', models.FloatField(default=-20.0, verbose_name='Dec Limit')),
                ('mag_limit', models.FloatField(default=12.0, verbose_name='Mag Limit')),
                ('hour_angle_range', models.FloatField(default=3.5, verbose_name='Hour Angle Range')),
                ('session_length', models.FloatField(default=3.0, verbose_name='Session Length')),
                ('show_planets', models.CharField(choices=[('visible', 'Only Above the Horizon'), ('all', 'All Planets')], default='visible', max_length=10, verbose_name='Show Planets')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='observe.observinglocation')),
            ],
        ),
    ]