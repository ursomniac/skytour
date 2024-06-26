# Generated by Django 4.2.9 on 2024-01-14 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dso", "0092_alter_dsoimage_use_in_carousel_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="dso",
            name="amateur_book_notes",
            field=models.TextField(blank=True, null=True, verbose_name="Book Notes"),
        ),
        migrations.AddField(
            model_name="dso",
            name="amateur_book_object",
            field=models.BooleanField(default=False, verbose_name="Use in Book"),
        ),
        migrations.AddField(
            model_name="dso",
            name="book_skill",
            field=models.CharField(
                blank=True, max_length=20, null=True, verbose_name="Skill Level"
            ),
        ),
        migrations.AddField(
            model_name="dsoinfield",
            name="amateur_book_notes",
            field=models.TextField(blank=True, null=True, verbose_name="Book Notes"),
        ),
        migrations.AddField(
            model_name="dsoinfield",
            name="amateur_book_object",
            field=models.BooleanField(default=False, verbose_name="Use in Book"),
        ),
        migrations.AddField(
            model_name="dsoinfield",
            name="book_skill",
            field=models.CharField(
                blank=True, max_length=20, null=True, verbose_name="Skill Level"
            ),
        ),
    ]
