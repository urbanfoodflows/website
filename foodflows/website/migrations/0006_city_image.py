# Generated by Django 5.0.2 on 2024-02-29 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_alter_datafile_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='cities/'),
        ),
    ]
