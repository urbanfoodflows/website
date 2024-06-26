# Generated by Django 5.0.2 on 2024-02-29 08:49

import django.db.models.deletion
import mdeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', mdeditor.fields.MDTextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'activities',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', mdeditor.fields.MDTextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cities',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='FoodGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', mdeditor.fields.MDTextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'foodgroups',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', mdeditor.fields.MDTextField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, max_length=100, null=True, unique=True)),
            ],
            options={
                'db_table': 'pages',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food', models.CharField(max_length=255)),
                ('year', models.PositiveSmallIntegerField()),
                ('quantity', models.IntegerField()),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('segment', models.CharField(blank=True, max_length=255, null=True)),
                ('sankey', models.BooleanField(db_index=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.city')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_from', to='website.city')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_to', to='website.city')),
                ('food_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.foodgroup')),
            ],
            options={
                'db_table': 'foodflows',
            },
        ),
        migrations.CreateModel(
            name='Population',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField()),
                ('population', models.IntegerField()),
                ('source', models.TextField()),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.city')),
            ],
            options={
                'db_table': 'population',
            },
        ),
    ]
