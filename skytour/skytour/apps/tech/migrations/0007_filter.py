# Generated by Django 4.0.2 on 2022-02-11 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tech', '0006_eyepiece_telescope'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Name')),
                ('filter_type', models.CharField(choices=[('wide', 'Wide'), ('narrow', 'Narrow')], max_length=40, verbose_name='Filter Type')),
                ('central_wavelength', models.FloatField(blank=True, help_text='in nm', null=True)),
                ('fwhm', models.FloatField(blank=True, help_text='in nm', null=True, verbose_name='FWHM')),
            ],
            options={
                'ordering': ['central_wavelength'],
            },
        ),
    ]
