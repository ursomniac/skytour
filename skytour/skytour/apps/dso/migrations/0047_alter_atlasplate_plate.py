# Generated by Django 4.0.4 on 2022-04-16 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dso', '0046_alter_dsolist_options_alter_dsolist_show_on_plan_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atlasplate',
            name='plate',
            field=models.ImageField(blank=True, null=True, upload_to='atlas_images', verbose_name='Plate'),
        ),
    ]
