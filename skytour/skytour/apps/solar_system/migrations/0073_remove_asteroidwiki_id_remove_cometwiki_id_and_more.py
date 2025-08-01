# Generated by Django 4.2.23 on 2025-06-24 00:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('solar_system', '0072_alter_asteroidwiki_object_alter_cometwiki_object_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asteroidwiki',
            name='id',
        ),
        migrations.RemoveField(
            model_name='cometwiki',
            name='id',
        ),
        migrations.RemoveField(
            model_name='meteorshowerwiki',
            name='id',
        ),
        migrations.RemoveField(
            model_name='planetwiki',
            name='id',
        ),
        migrations.AlterField(
            model_name='asteroidwiki',
            name='object',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='wiki', serialize=False, to='solar_system.asteroid'),
        ),
        migrations.AlterField(
            model_name='cometwiki',
            name='object',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='wiki', serialize=False, to='solar_system.comet'),
        ),
        migrations.AlterField(
            model_name='meteorshowerwiki',
            name='object',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='wiki', serialize=False, to='solar_system.meteorshower'),
        ),
        migrations.AlterField(
            model_name='planetwiki',
            name='object',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='wiki', serialize=False, to='solar_system.planet'),
        ),
    ]
