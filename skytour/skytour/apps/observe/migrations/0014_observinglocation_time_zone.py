# Generated by Django 4.0 on 2022-01-03 22:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('misc', '0002_alter_stateregion_options_alter_timezone_options'),
        ('observe', '0013_rename_time_zone_observinglocation_x_time_zone'),
    ]

    operations = [
        migrations.AddField(
            model_name='observinglocation',
            name='time_zone',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='misc.timezone'),
            preserve_default=False,
        ),
    ]
