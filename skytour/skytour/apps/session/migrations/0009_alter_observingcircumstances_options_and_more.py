# Generated by Django 4.0.2 on 2022-02-10 18:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('observe', '0017_remove_observinglocation_x_state'),
        ('session', '0008_observingcircumstances_sqm'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='observingcircumstances',
            options={'ordering': ['ut_datetime'], 'verbose_name': 'Conditions', 'verbose_name_plural': 'Observing Conditions'},
        ),
        migrations.AlterModelOptions(
            name='observingsession',
            options={'ordering': ['-ut_date', '-pk']},
        ),
        migrations.RenameField(
            model_name='observingcircumstances',
            old_name='utdt',
            new_name='ut_datetime',
        ),
        migrations.AlterUniqueTogether(
            name='observingsession',
            unique_together={('ut_date', 'location')},
        ),
    ]