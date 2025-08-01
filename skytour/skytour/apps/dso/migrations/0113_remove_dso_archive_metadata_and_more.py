# Generated by Django 4.2.19 on 2025-02-16 15:52

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dso', '0112_alter_dsoobservation_ut_datetime'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dso',
            name='archive_metadata',
        ),
        migrations.RemoveField(
            model_name='dsoinfield',
            name='archive_metadata',
        ),
        migrations.AddField(
            model_name='dso',
            name='override_metadata',
            field=jsonfield.fields.JSONField(blank=True, help_text='Custom JSON Objects - overrides SIMBAD/HyperLeda values', null=True),
        ),
        migrations.AddField(
            model_name='dsoinfield',
            name='override_metadata',
            field=jsonfield.fields.JSONField(blank=True, help_text='Custom JSON Objects - overrides SIMBAD/HyperLeda values', null=True),
        ),
        migrations.AlterField(
            model_name='dso',
            name='angular_size',
            field=models.CharField(blank=True, help_text='single or double dimension, e.g., 36" or  8\'x5\'', max_length=50, null=True, verbose_name='Angular Size'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='dso_finder_chart',
            field=models.ImageField(blank=True, help_text='This is a printable color finder chart', null=True, upload_to='dso_finder_chart', verbose_name='DSO Finder Chart'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='dso_finder_chart_narrow',
            field=models.ImageField(blank=True, help_text='Generate narrow-field chart', null=True, upload_to='dso_finder_narrow', verbose_name='Constructed Finder Chart - Narrow'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='dso_finder_chart_wide',
            field=models.ImageField(blank=True, help_text='Generated wide-field chart', null=True, upload_to='dso_finder_wide', verbose_name='Constructed Finder Chart - Wide'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='dso_imaging_chart',
            field=models.ImageField(blank=True, help_text='Generated field from Stellarium', null=True, upload_to='dso_imaging_charts', verbose_name='Imaging Chart for eQuinox 2'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='finder_chart',
            field=models.ImageField(blank=True, help_text='Deprecated: finder charts found on the WWW', null=True, upload_to='finder_chart/', verbose_name='Finder Chart'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='hyperleda_name',
            field=models.CharField(blank=True, help_text='Use this designation when querying HyperLeda', max_length=30, null=True, verbose_name='HyperLeda Name Override'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='magnitude_system',
            field=models.CharField(blank=True, help_text='e.g., V, B, Phot.', max_length=3, null=True, verbose_name='Mag. System'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='map_label',
            field=models.CharField(blank=True, help_text='Override label used on maps/atlas plates', max_length=40, null=True, verbose_name='Map Label'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='metadata',
            field=jsonfield.fields.JSONField(blank=True, help_text='JSON object constructed from HyperLeda lookup', null=True),
        ),
        migrations.AlterField(
            model_name='dso',
            name='nickname',
            field=models.CharField(blank=True, help_text='A nickname, e.g. "Crab Nebula"', max_length=200, null=True, verbose_name='Nickname'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='other_parameters',
            field=models.TextField(blank=True, help_text='Age, etc., in x: y; format - see README', null=True, verbose_name='Other Params'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='pdf_page',
            field=models.FileField(blank=True, help_text='PDF file --- deprecated?', null=True, upload_to='dso_pdf', verbose_name='PDF Page'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='priority',
            field=models.CharField(blank=True, choices=[('Highest', '4 - Highest'), ('High', '3 - High'), ('Medium', '2 -Medium'), ('Low', '1 - Low'), ('None', '0 - None')], help_text='DEPRECATED', max_length=20, null=True, verbose_name='Priority'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='show_on_skymap',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes')], default=0, help_text='Filter for DSOs on skymap', verbose_name='Show on Skymap'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='shown_name',
            field=models.CharField(blank=True, help_text='Override if you want to use a specific designation', max_length=100, null=True, verbose_name='Shown Name'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='simbad',
            field=jsonfield.fields.JSONField(blank=True, help_text='JSON object constructed from SIMBAD lookup', null=True),
        ),
        migrations.AlterField(
            model_name='dso',
            name='simbad_name',
            field=models.CharField(blank=True, help_text='Use this designation when querying SIMBAD', max_length=30, null=True, verbose_name='SIMBAD Name Override'),
        ),
        migrations.AlterField(
            model_name='dso',
            name='surface_brightness',
            field=models.FloatField(blank=True, help_text='Mag/arcmin^2 (SQM)', null=True, verbose_name='Surface Brightness'),
        ),
        migrations.AlterField(
            model_name='dsoimage',
            name='exposure',
            field=models.FloatField(blank=True, help_text='in floating minutes', null=True, verbose_name='Image Exposure'),
        ),
        migrations.AlterField(
            model_name='dsoinfield',
            name='angular_size',
            field=models.CharField(blank=True, help_text='single or double dimension, e.g., 36" or  8\'x5\'', max_length=50, null=True, verbose_name='Angular Size'),
        ),
        migrations.AlterField(
            model_name='dsoinfield',
            name='hyperleda_name',
            field=models.CharField(blank=True, help_text='Use this designation when querying HyperLeda', max_length=30, null=True, verbose_name='HyperLeda Name Override'),
        ),
        migrations.AlterField(
            model_name='dsoinfield',
            name='magnitude_system',
            field=models.CharField(blank=True, help_text='e.g., V, B, Phot.', max_length=3, null=True, verbose_name='Mag. System'),
        ),
        migrations.AlterField(
            model_name='dsoinfield',
            name='metadata',
            field=jsonfield.fields.JSONField(blank=True, help_text='JSON object constructed from HyperLeda lookup', null=True),
        ),
        migrations.AlterField(
            model_name='dsoinfield',
            name='nickname',
            field=models.CharField(blank=True, help_text='A nickname, e.g. "Crab Nebula"', max_length=200, null=True, verbose_name='Nickname'),
        ),
        migrations.AlterField(
            model_name='dsoinfield',
            name='other_parameters',
            field=models.TextField(blank=True, help_text='Age, etc., in x: y; format - see README', null=True, verbose_name='Other Params'),
        ),
        migrations.AlterField(
            model_name='dsoinfield',
            name='shown_name',
            field=models.CharField(blank=True, help_text='Override if you want to use a specific designation', max_length=100, null=True, verbose_name='Shown Name'),
        ),
        migrations.AlterField(
            model_name='dsoinfield',
            name='simbad',
            field=jsonfield.fields.JSONField(blank=True, help_text='JSON object constructed from SIMBAD lookup', null=True),
        ),
        migrations.AlterField(
            model_name='dsoinfield',
            name='simbad_name',
            field=models.CharField(blank=True, help_text='Use this designation when querying SIMBAD', max_length=30, null=True, verbose_name='SIMBAD Name Override'),
        ),
        migrations.AlterField(
            model_name='dsoinfield',
            name='surface_brightness',
            field=models.FloatField(blank=True, help_text='Mag/arcmin^2 (SQM)', null=True, verbose_name='Surface Brightness'),
        ),
        migrations.AlterField(
            model_name='dsolibraryimage',
            name='exposure',
            field=models.FloatField(blank=True, help_text='in floating minutes', null=True, verbose_name='Image Exposure'),
        ),
        migrations.AlterField(
            model_name='dsolist',
            name='active_observing_list',
            field=models.PositiveIntegerField(choices=[(0, 'No'), (1, 'Yes')], default=0, help_text='This is used for a back-reference on lists of DSOs', verbose_name='Active List'),
        ),
        migrations.AlterField(
            model_name='dsolist',
            name='map_scaling_factor',
            field=models.FloatField(default=2.4, help_text='Map scaling: you prob. do not need to change this.', verbose_name='Map Scaling Factor'),
        ),
    ]
