# Generated by Django 4.2.11 on 2024-05-26 16:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0011_takeleave_total_hour_takeleave_total_minute_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineuser',
            name='become_staff_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 27, 0, 26, 0, 888982)),
        ),
        migrations.AlterField(
            model_name='staffschedule',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 27, 0, 26, 0, 888982)),
        ),
    ]
