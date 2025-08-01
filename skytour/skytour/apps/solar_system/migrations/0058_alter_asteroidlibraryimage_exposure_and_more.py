# Generated by Django 4.2.19 on 2025-02-16 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar_system', '0057_alter_comet_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asteroidlibraryimage',
            name='exposure',
            field=models.FloatField(blank=True, help_text='in floating minutes', null=True, verbose_name='Image Exposure'),
        ),
        migrations.AlterField(
            model_name='cometlibraryimage',
            name='exposure',
            field=models.FloatField(blank=True, help_text='in floating minutes', null=True, verbose_name='Image Exposure'),
        ),
        migrations.AlterField(
            model_name='planetlibraryimage',
            name='exposure',
            field=models.FloatField(blank=True, help_text='in floating minutes', null=True, verbose_name='Image Exposure'),
        ),
    ]
