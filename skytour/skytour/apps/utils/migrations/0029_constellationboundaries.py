# Generated by Django 4.0.4 on 2022-05-13 13:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0028_constellationvertex'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConstellationBoundaries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ra', models.FloatField(verbose_name='Start R.A.')),
                ('dec', models.FloatField(verbose_name='Start Dec.')),
                ('end_vertex', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vertex_end', to='utils.constellationvertex')),
                ('start_vertex', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vertex_start', to='utils.constellationvertex')),
            ],
        ),
    ]