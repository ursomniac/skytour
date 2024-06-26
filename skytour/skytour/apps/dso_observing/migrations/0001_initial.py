# Generated by Django 4.2.9 on 2024-01-20 18:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("dso", "0095_remove_dso_amateur_book_notes_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TargetDSO",
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
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[(-9, "Removed"), (0, "Offline"), (1, "Active")],
                        default=1,
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "dso",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="dso.dso"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TargetObservingMode",
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
                (
                    "mode",
                    models.CharField(
                        choices=[
                            ("N", "Naked Eye"),
                            ("B", "Binoculars"),
                            ("S", "Small Scope"),
                            ("M", "Medium Scope"),
                            ("I", "Imaging Scope"),
                        ],
                        max_length=10,
                        verbose_name="Observing Mode",
                    ),
                ),
                (
                    "viable",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Not Viable"),
                            (1, "Unlikely Viable"),
                            (2, "Extreme Difficulty"),
                            (3, "Very Difficult"),
                            (4, "Challenging"),
                            (5, "Requires Patience"),
                            (6, "Generally Visible"),
                            (7, "Usually Easy"),
                            (8, "Easy"),
                            (9, "Very Easy"),
                            (10, "Extremely easy"),
                        ],
                        max_length=20,
                        verbose_name="Viability",
                    ),
                ),
                (
                    "priority",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        choices=[
                            (0, "None"),
                            (1, "Low"),
                            (2, "Medium"),
                            (3, "High"),
                            (4, "Highest"),
                        ],
                        null=True,
                    ),
                ),
                ("interesting", models.BooleanField(default=False)),
                ("challenging", models.BooleanField(default=False)),
                (
                    "issues",
                    models.CharField(
                        blank=True,
                        help_text="Comma separated list of codes - other issues in notes or quoted",
                        max_length=250,
                        null=True,
                        verbose_name="Challenge Codes",
                    ),
                ),
                (
                    "description_flags",
                    models.CharField(
                        blank=True,
                        help_text="Comma-separated list of codes - other issues in notes or quoted",
                        max_length=250,
                        null=True,
                        verbose_name="Description Flags",
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "target",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dso_observing.targetdso",
                    ),
                ),
            ],
        ),
    ]
