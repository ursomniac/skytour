# Generated by Django 4.0.4 on 2022-05-13 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0011_observingcircumstances_notes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='observingcircumstances',
            options={'ordering': ['-ut_datetime'], 'verbose_name': 'Conditions', 'verbose_name_plural': 'Observing Conditions'},
        ),
        migrations.AlterModelOptions(
            name='observingsession',
            options={'ordering': ['-pk']},
        ),
    ]