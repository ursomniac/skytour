# Generated by Django 4.0.4 on 2022-05-13 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0027_starcatalog'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConstellationVertex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ra_1875', models.FloatField(verbose_name='R.A. 1875')),
                ('dec_1875', models.FloatField(verbose_name='Dec. 1875')),
                ('constellation', models.ManyToManyField(to='utils.constellation')),
            ],
        ),
    ]
