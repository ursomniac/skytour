# Generated by Django 4.0.4 on 2023-09-04 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('observe', '0019_observinglocation_pdf_form'),
        ('dso', '0079_alter_dsoimagingchecklist_priority'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dsoimage',
            name='amateur_image',
        ),
        migrations.RemoveField(
            model_name='dsoimage',
            name='own_image',
        ),
        migrations.RemoveField(
            model_name='dsolibraryimage',
            name='amateur_image',
        ),
        migrations.RemoveField(
            model_name='dsolibraryimage',
            name='own_image',
        ),
        migrations.AlterField(
            model_name='dsoobservation',
            name='location',
            field=models.ForeignKey(default=1, limit_choices_to={'status__in': ['Active', 'Provisional']}, on_delete=django.db.models.deletion.CASCADE, to='observe.observinglocation'),
        ),
    ]