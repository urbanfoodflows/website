# Generated by Django 5.0.2 on 2024-04-10 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0024_foodgroup_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='idealconsumption',
            name='color',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]