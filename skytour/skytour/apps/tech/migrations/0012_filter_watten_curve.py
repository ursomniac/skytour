# Generated by Django 4.0.2 on 2022-02-11 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tech', '0011_filter_tech_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter',
            name='watten_curve',
            field=models.ImageField(blank=True, null=True, upload_to='filter_specs', verbose_name='Watten Curve'),
        ),
    ]
