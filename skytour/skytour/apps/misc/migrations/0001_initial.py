# Generated by Django 4.0 on 2022-01-03 22:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
            ],
        ),
        migrations.CreateModel(
            name='StateRegion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Name')),
                ('slug', models.SlugField(help_text='Put the abbreviation here.', verbose_name='Slug')),
            ],
        ),
        migrations.CreateModel(
            name='TimeZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Name')),
                ('utc_offset', models.IntegerField(help_text='<0 for West, >0 for East of Greenwich', verbose_name='UTC Offset')),
            ],
        ),
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='Dates are assumed to be UT', verbose_name='Date')),
                ('time', models.TimeField(blank=True, help_text='Times are assumed to be UT', null=True, verbose_name='Time')),
                ('event', models.CharField(max_length=100, verbose_name='Event')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='misc.eventtype')),
            ],
        ),
    ]
