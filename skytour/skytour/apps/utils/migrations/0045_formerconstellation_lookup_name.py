# Generated by Django 4.2.23 on 2025-06-22 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0044_formerconstellation'),
    ]

    operations = [
        migrations.AddField(
            model_name='formerconstellation',
            name='lookup_name',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Lookup Name'),
        ),
    ]
