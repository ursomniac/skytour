# Generated by Django 4.0.2 on 2022-02-13 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_parameter', '0003_siteparameterlink_new_window'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteparameterfloat',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='siteparameterimage',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='siteparameterlink',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='siteparameternumber',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='siteparameterpositiveinteger',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='siteparameterstring',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
    ]