# Generated by Django 5.0.2 on 2024-04-06 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0023_city_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodgroup',
            name='color',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]