# Generated by Django 4.0.1 on 2022-01-29 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0019_alter_objecttype_map_symbol_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
    ]