# Generated by Django 4.2.11 on 2024-06-17 03:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0027_rename_product_name_item_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='amount',
        ),
        migrations.AlterField(
            model_name='reservation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 17, 11, 18, 41, 120412)),
        ),
    ]
