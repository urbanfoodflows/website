# Generated by Django 5.0.2 on 2024-04-06 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0021_idealconsumption'),
    ]

    operations = [
        migrations.AddField(
            model_name='idealconsumption',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
