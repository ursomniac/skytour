# Generated by Django 4.2.23 on 2025-06-22 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0049_alter_catalog_lookup_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='lookup_mode',
            field=models.CharField(choices=[('abbreviation', 'Abbreviation'), ('name', 'Catalog Name'), ('constellation', 'By Constellation'), ('custom', 'Custom')], default='abbreviation', help_text='for lookups like Wikipedia', max_length=40, verbose_name='Lookup Mode'),
        ),
    ]
