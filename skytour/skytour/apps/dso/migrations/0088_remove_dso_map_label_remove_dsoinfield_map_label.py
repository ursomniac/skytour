# Generated by Django 4.0.4 on 2023-10-21 00:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dso', '0087_dso_map_label_dsoinfield_map_label'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dso',
            name='map_label',
        ),
        migrations.RemoveField(
            model_name='dsoinfield',
            name='map_label',
        ),
    ]