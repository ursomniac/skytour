# Generated by Django 4.2.19 on 2025-02-17 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0017_alter_observingcircumstances_ut_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observingcircumstances',
            name='moon',
            field=models.BooleanField(default=False, help_text='Set if Moon is above the horizon', verbose_name='Moon'),
        ),
        migrations.AlterField(
            model_name='observingcircumstances',
            name='use_sqm',
            field=models.PositiveIntegerField(choices=[(1, 'Yes'), (0, 'No')], default=1, help_text='Set to No if it will skew the stats', verbose_name='Use SQM in Stats'),
        ),
        migrations.AlterField(
            model_name='observingsession',
            name='ut_date',
            field=models.DateField(help_text='YYYY-MM-DD', verbose_name='UT Date'),
        ),
    ]
