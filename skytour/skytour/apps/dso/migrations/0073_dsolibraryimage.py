# Generated by Django 4.0.4 on 2023-07-30 00:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dso', '0072_alter_dsoobservation_imaging_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DSOLibraryImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='object_image/', verbose_name='Image')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('order_in_list', models.PositiveIntegerField(default=1, verbose_name='Order')),
                ('amateur_image', models.BooleanField(default=None, null=True, verbose_name='Amateur Image')),
                ('own_image', models.PositiveIntegerField(choices=[(1, 'Yes'), (0, 'No')], default=0, verbose_name='My Own Image')),
                ('exposure', models.FloatField(blank=True, null=True, verbose_name='Image Exposure')),
                ('processing_status', models.CharField(blank=True, choices=[('None', 'Not Yet Started'), ('DB', 'Processed image added to DB'), ('Rejected', 'Image Rejected'), ('Unknown', 'Unknown')], max_length=30, null=True, verbose_name='Image Processing Status')),
                ('ut_datetime', models.DateTimeField()),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image_library', to='dso.dso')),
            ],
            options={
                'verbose_name': 'Library Images',
            },
        ),
    ]