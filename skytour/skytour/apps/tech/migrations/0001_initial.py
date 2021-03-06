# Generated by Django 4.0.1 on 2022-01-23 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Telescope',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('aperture', models.PositiveIntegerField(help_text='mm', verbose_name='Aperture')),
                ('focal_length', models.PositiveIntegerField(help_text='mm', verbose_name='Focal Length')),
            ],
        ),
    ]
