# Generated by Django 4.0.1 on 2022-02-03 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0004_observingsession_cloud_cover_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observingsession',
            name='seeing',
            field=models.PositiveIntegerField(blank=True, choices=[(5, 'Excellent: stable diffraction rings'), (4, 'Good: light undulations across diffraction rings'), (3, 'Fair: broken diffraction rings; central disk deformations'), (2, 'Poor: (partly) missing diffraction rings; eddy streams in central disk'), (1, 'Fail: boiling image; no sign of diffraction pattern')], help_text='1 (poor) to 5 (excellent)', null=True, verbose_name='Seeing'),
        ),
    ]