# Generated by Django 4.0.1 on 2022-01-16 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_parameter', '0002_rename_siteparamterlink_siteparameterlink_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteparameterlink',
            name='new_window',
            field=models.BooleanField(blank=True, default=True, null=True, verbose_name='Opens New Window'),
        ),
    ]
