# Generated by Django 4.0.1 on 2022-01-17 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0010_objecttype_marker_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='constellation',
            name='map',
            field=models.ImageField(blank=True, null=True, upload_to='constellation_maps', verbose_name='Map'),
        ),
        migrations.AddField(
            model_name='constellation',
            name='other_map',
            field=models.ImageField(blank=True, null=True, upload_to='constellation_maps', verbose_name='Map'),
        ),
    ]