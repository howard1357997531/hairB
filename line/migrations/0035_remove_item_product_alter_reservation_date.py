# Generated by Django 4.2.11 on 2024-06-21 01:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0034_item_image_url_item_price_alter_reservation_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='product',
        ),
        migrations.AlterField(
            model_name='reservation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 21, 9, 26, 12, 540221)),
        ),
    ]
