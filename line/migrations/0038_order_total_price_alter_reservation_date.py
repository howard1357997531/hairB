# Generated by Django 4.2.11 on 2024-06-21 01:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0037_alter_item_name_alter_reservation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 21, 9, 43, 57, 13655)),
        ),
    ]
