# Generated by Django 4.0.4 on 2022-12-24 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar_system', '0033_asteroidobservation_session_cometobservation_session_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='meteorshower',
            name='intenside',
            field=models.CharField(choices=[('Major', 'Major'), ('Minor', 'Minor'), ('Sporadic', 'Sporadic')], default='Major', max_length=20, verbose_name='Intensity'),
        ),
    ]
