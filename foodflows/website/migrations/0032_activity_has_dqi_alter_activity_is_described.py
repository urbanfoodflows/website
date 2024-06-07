# Generated by Django 5.0.2 on 2024-04-30 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0031_activity_is_active_activity_is_described'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='has_dqi',
            field=models.BooleanField(db_index=True, default=True, help_text='Indicates if this activity can have DQIs'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='is_described',
            field=models.BooleanField(db_index=True, default=True, help_text='Indicates if this is used for data descriptions'),
        ),
    ]