# Generated by Django 4.0.2 on 2022-02-11 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tech', '0007_filter'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='Notes'),
        ),
    ]
