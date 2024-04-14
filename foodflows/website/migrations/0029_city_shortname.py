# Generated by Django 5.0.2 on 2024-04-14 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0028_activity_shortname'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='shortname',
            field=models.CharField(blank=True, help_text='This is shown in tables where space is tight. Normally 4 letters, all-caps.', max_length=4, null=True),
        ),
    ]