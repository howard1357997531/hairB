# Generated by Django 4.2.11 on 2024-05-21 08:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0005_alter_reservation_date_check'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='date_check',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='time',
        ),
        migrations.AlterField(
            model_name='reservation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 21, 16, 25, 51, 719180)),
        ),
    ]
