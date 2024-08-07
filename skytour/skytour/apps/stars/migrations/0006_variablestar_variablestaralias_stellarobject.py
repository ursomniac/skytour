# Generated by Django 4.0.4 on 2023-12-13 02:32

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0031_alter_catalog_options'),
        ('stars', '0005_doublestar_catalog_doublestar_distance_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VariableStar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ra_h', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(23)], verbose_name='RA: hr')),
                ('ra_m', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(59)], verbose_name='min')),
                ('ra_s', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(59.9999999)], verbose_name='sec')),
                ('ra', models.FloatField(blank=True, null=True, verbose_name='R.A.')),
                ('ra_text', models.CharField(blank=True, max_length=16, null=True, verbose_name='R.A. Text')),
                ('dec_sign', models.CharField(choices=[('+', '+'), ('-', '-')], max_length=1, verbose_name='Dec: Sign')),
                ('dec_d', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(89)], verbose_name='deg')),
                ('dec_m', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(59)], verbose_name='min')),
                ('dec_s', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(59.9999999)], verbose_name='sec')),
                ('dec', models.FloatField(blank=True, null=True, verbose_name='Dec.')),
                ('dec_text', models.CharField(blank=True, max_length=16, null=True, verbose_name='Dec. Text')),
                ('id_in_catalog', models.CharField(blank=True, help_text='ccnNNNd: cc=const, nNNN is V*# or greek/bayer/flamsteed d is component', max_length=7, null=True, verbose_name='GCVS ID')),
                ('mag_code', models.CharField(blank=True, max_length=2, null=True, verbose_name='Mag Code')),
                ('mag_max', models.FloatField(blank=True, null=True, verbose_name='Mag Max')),
                ('mag_max_limit', models.CharField(blank=True, max_length=1, null=True, verbose_name='Mag Max Limit')),
                ('mag_max_uncertainty', models.CharField(blank=True, max_length=1, null=True, verbose_name='Mag Max Unc')),
                ('mag_min1', models.FloatField(blank=True, null=True, verbose_name='Mag Min 1')),
                ('mag_min1_limit', models.CharField(blank=True, max_length=1, null=True, verbose_name='Mag Min 1 Limit')),
                ('mag_min1_uncertainty', models.CharField(blank=True, max_length=1, null=True, verbose_name='Mag Min 1 Unc')),
                ('mag_min1_system', models.CharField(blank=True, max_length=2, null=True, verbose_name='Mag Min 1 System')),
                ('mag_min1_amplitude', models.FloatField(verbose_name='Min 1 Amplitude')),
                ('mag_min2', models.FloatField(blank=True, null=True, verbose_name='Mag Min 2')),
                ('mag_min2_limit', models.CharField(blank=True, max_length=1, null=True, verbose_name='Mag Min 2 Limit')),
                ('mag_min2_uncertainty', models.CharField(blank=True, max_length=1, null=True, verbose_name='Mag Min 2 Unc')),
                ('mag_min2_system', models.CharField(blank=True, max_length=2, null=True, verbose_name='Mag Min 2 System')),
                ('mag_min2_amplitude', models.FloatField(verbose_name='Min 2 Amplitude')),
                ('period', models.FloatField(blank=True, help_text='days', null=True, verbose_name='Period')),
                ('period_uncertainty', models.CharField(blank=True, max_length=5, null=True, verbose_name='Period Unc.')),
                ('type_original', models.CharField(blank=True, max_length=10, null=True, verbose_name='Type')),
                ('type_revised', models.CharField(blank=True, max_length=10, null=True, verbose_name='New Type')),
                ('spectral_type', models.CharField(blank=True, max_length=20, null=True, verbose_name='Spectral Type')),
                ('bsc_id', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='stars.brightstar')),
                ('catalog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utils.starcatalog')),
                ('constellation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='utils.constellation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VariableStarAlias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_in_catalog', models.CharField(max_length=24, verbose_name='ID')),
                ('shown_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Shown Name')),
                ('catalog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utils.starcatalog')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='stars.variablestar')),
            ],
            options={
                'verbose_name': 'Variable Star Alias',
                'verbose_name_plural': 'Variable Star Aliases',
            },
        ),
        migrations.CreateModel(
            name='StellarObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ra_h', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(23)], verbose_name='RA: hr')),
                ('ra_m', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(59)], verbose_name='min')),
                ('ra_s', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(59.9999999)], verbose_name='sec')),
                ('ra', models.FloatField(blank=True, null=True, verbose_name='R.A.')),
                ('ra_text', models.CharField(blank=True, max_length=16, null=True, verbose_name='R.A. Text')),
                ('dec_sign', models.CharField(choices=[('+', '+'), ('-', '-')], max_length=1, verbose_name='Dec: Sign')),
                ('dec_d', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(89)], verbose_name='deg')),
                ('dec_m', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(59)], verbose_name='min')),
                ('dec_s', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(59.9999999)], verbose_name='sec')),
                ('dec', models.FloatField(blank=True, null=True, verbose_name='Dec.')),
                ('dec_text', models.CharField(blank=True, max_length=16, null=True, verbose_name='Dec. Text')),
                ('catalog', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='utils.starcatalog')),
                ('constellation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='utils.constellation')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
