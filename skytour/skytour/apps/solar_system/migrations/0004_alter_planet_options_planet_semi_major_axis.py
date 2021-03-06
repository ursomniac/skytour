# Generated by Django 4.0 on 2022-01-01 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar_system', '0003_planet_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='planet',
            options={'ordering': ['semi_major_axis']},
        ),
        migrations.AddField(
            model_name='planet',
            name='semi_major_axis',
            field=models.FloatField(blank=True, help_text='au', null=True, verbose_name='Semi-Major Axis'),
        ),
    ]
