# Generated by Django 4.2.9 on 2024-01-20 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dso_observing", "0002_alter_targetobservingmode_viable"),
    ]

    operations = [
        migrations.AddField(
            model_name="targetdso",
            name="ready_to_go",
            field=models.BooleanField(default=False),
        ),
    ]