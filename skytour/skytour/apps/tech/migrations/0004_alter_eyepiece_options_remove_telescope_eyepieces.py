# Generated by Django 4.0.1 on 2022-01-23 19:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tech', '0003_eyepiece_eyepiecetelescope_telescope_eyepieces'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eyepiece',
            options={'ordering': ['-focal_length']},
        ),
        migrations.RemoveField(
            model_name='telescope',
            name='eyepieces',
        ),
    ]
