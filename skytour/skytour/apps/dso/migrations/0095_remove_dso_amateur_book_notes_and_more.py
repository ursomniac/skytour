# Generated by Django 4.2.9 on 2024-01-14 22:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dso", "0094_remove_dsoinfield_amateur_book_notes_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dso",
            name="amateur_book_notes",
        ),
        migrations.RemoveField(
            model_name="dso",
            name="amateur_book_object",
        ),
        migrations.RemoveField(
            model_name="dso",
            name="book_skill",
        ),
    ]