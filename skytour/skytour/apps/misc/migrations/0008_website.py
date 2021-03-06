# Generated by Django 4.0.1 on 2022-01-10 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('misc', '0007_alter_eventtype_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('url', models.URLField(verbose_name='URL')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
