# Generated by Django 4.0.4 on 2022-07-31 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0014_alter_observingsession_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='observingcircumstances',
            name='use_sqm',
            field=models.PositiveIntegerField(choices=[(1, 'Yes'), (0, 'No')], default=1, verbose_name='Use SQM in Stats'),
        ),
    ]
