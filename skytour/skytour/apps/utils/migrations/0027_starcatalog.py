# Generated by Django 4.0.4 on 2022-04-15 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0026_objecttype_short_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='StarCatalog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Catalog Name')),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('abbreviation', models.CharField(max_length=10, verbose_name='Abbreviation')),
                ('use_abbr', models.BooleanField(default=True, verbose_name='Use Abbr in List')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]