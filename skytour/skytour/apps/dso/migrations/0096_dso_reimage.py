# Generated by Django 4.2.9 on 2024-02-02 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dso", "0095_remove_dso_amateur_book_notes_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="dso",
            name="reimage",
            field=models.BooleanField(
                default=False, help_text="Check to override image filtering."
            ),
        ),
    ]
