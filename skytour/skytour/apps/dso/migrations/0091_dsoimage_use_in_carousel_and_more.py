# Generated by Django 4.2.9 on 2024-01-06 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dso", "0090_alter_dso_distance_units_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="dsoimage",
            name="use_in_carousel",
            field=models.PositiveIntegerField(
                choices=[(1, "Yes"), (0, "No")],
                default=1,
                help_text="Set to YES/1 show on the image carousel",
                verbose_name="On Plan PDF",
            ),
        ),
        migrations.AddField(
            model_name="dsolibraryimage",
            name="use_in_carousel",
            field=models.PositiveIntegerField(
                choices=[(1, "Yes"), (0, "No")],
                default=1,
                help_text="Set to YES/1 show on the image carousel",
                verbose_name="On Plan PDF",
            ),
        ),
        migrations.AlterField(
            model_name="dsoimage",
            name="processing_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("None", "Not Yet Started"),
                    ("Default", "Default Unistellar Image"),
                    ("3-Step", "3-Step: Dark, Stretched, Cleaned"),
                    ("DB", "Processed image added to DB"),
                    ("Rejected", "Image Rejected"),
                    ("Unknown", "Unknown"),
                ],
                max_length=30,
                null=True,
                verbose_name="Image Processing Status",
            ),
        ),
        migrations.AlterField(
            model_name="dsolibraryimage",
            name="processing_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("None", "Not Yet Started"),
                    ("Default", "Default Unistellar Image"),
                    ("3-Step", "3-Step: Dark, Stretched, Cleaned"),
                    ("DB", "Processed image added to DB"),
                    ("Rejected", "Image Rejected"),
                    ("Unknown", "Unknown"),
                ],
                max_length=30,
                null=True,
                verbose_name="Image Processing Status",
            ),
        ),
    ]
