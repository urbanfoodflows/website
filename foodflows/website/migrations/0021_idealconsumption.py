# Generated by Django 5.0.2 on 2024-04-04 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0020_foodgroup_ideal_consumption'),
    ]

    operations = [
        migrations.CreateModel(
            name='IdealConsumption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(blank=True, help_text='Ideal per capita consumption (g/day)', null=True)),
                ('foodgroups', models.ManyToManyField(to='website.foodgroup')),
            ],
            options={
                'db_table': 'idealconsumption',
                'ordering': ['id'],
            },
        ),
    ]
