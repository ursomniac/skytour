# Generated by Django 4.2.9 on 2024-06-30 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dso", "0107_dso_other_parameters_dsoinfield_other_parameters"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dso",
            name="other_parameters",
            field=models.TextField(
                blank=True,
                help_text="Age, etc., in x: y; format",
                null=True,
                verbose_name="Other Params",
            ),
        ),
        migrations.AlterField(
            model_name="dsoinfield",
            name="other_parameters",
            field=models.TextField(
                blank=True,
                help_text="Age, etc., in x: y; format",
                null=True,
                verbose_name="Other Params",
            ),
        ),
    ]