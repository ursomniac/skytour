# Generated by Django 4.2.9 on 2024-08-07 22:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("utils", "0036_alter_objecttype_map_symbol_type"),
        ("dso", "0108_alter_dso_other_parameters_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="DSOInFieldAlias",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("id_in_catalog", models.CharField(max_length=24, verbose_name="ID")),
                (
                    "alias_in_field",
                    models.PositiveIntegerField(
                        choices=[(0, "No"), (1, "Yes")],
                        default=0,
                        help_text="Alias is for a field object.",
                        verbose_name="Alias in Field",
                    ),
                ),
                (
                    "in_field_dso",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        verbose_name="In Field DSO Name",
                    ),
                ),
                (
                    "shown_name",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="Shown Name"
                    ),
                ),
                (
                    "catalog",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="utils.catalog"
                    ),
                ),
                (
                    "object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aliases",
                        to="dso.dsoinfield",
                    ),
                ),
            ],
            options={
                "verbose_name": "Alias",
                "verbose_name_plural": "Aliases",
                "abstract": False,
            },
        ),
    ]
