# Generated by Django 4.0.2 on 2022-02-11 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0009_alter_observingcircumstances_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='observingcircumstances',
            name='wind',
            field=models.CharField(blank=True, help_text='Speed/Direction', max_length=50, null=True, verbose_name='Wind'),
        ),
    ]