# Generated by Django 5.0.2 on 2024-03-18 08:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_city_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_from', to='website.activity'),
        ),
        migrations.AlterField(
            model_name='data',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_to', to='website.activity'),
        ),
    ]
