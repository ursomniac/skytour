# Generated by Django 4.2.19 on 2025-02-27 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dso', '0119_delete_dsoimagingchecklist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dsoimage',
            name='image_style',
            field=models.CharField(blank=True, choices=[('square', 'Square/Library Image Carousel'), ('map', 'Annotated Image/Full Frame Carousel'), ('full', 'Full Frame Image/Full Frame Carousel'), ('other', 'Other')], max_length=30, null=True, verbose_name='Image Class'),
        ),
        migrations.AlterField(
            model_name='dsolibraryimage',
            name='image_style',
            field=models.CharField(blank=True, choices=[('square', 'Square/Library Image Carousel'), ('map', 'Annotated Image/Full Frame Carousel'), ('full', 'Full Frame Image/Full Frame Carousel'), ('other', 'Other')], max_length=30, null=True, verbose_name='Image Class'),
        ),
    ]
