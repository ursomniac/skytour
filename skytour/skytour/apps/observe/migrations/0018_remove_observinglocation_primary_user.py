# Generated by Django 4.0.2 on 2022-02-13 15:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('observe', '0017_remove_observinglocation_x_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='observinglocation',
            name='primary_user',
        ),
    ]