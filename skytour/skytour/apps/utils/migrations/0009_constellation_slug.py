# Generated by Django 3.2.9 on 2021-11-20 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0008_alter_constellation_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='constellation',
            name='slug',
            field=models.SlugField(default='xxx', verbose_name='Slug'),
        ),
    ]
