# Generated by Django 4.2.11 on 2024-05-21 17:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_alter_staffschedule_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffschedule',
            name='is_full',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='staffschedule',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 22, 1, 45, 57, 814538)),
        ),
    ]
