# Generated by Django 4.0.4 on 2022-04-30 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0010_observingcircumstances_wind'),
    ]

    operations = [
        migrations.AddField(
            model_name='observingcircumstances',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='Notes'),
        ),
    ]