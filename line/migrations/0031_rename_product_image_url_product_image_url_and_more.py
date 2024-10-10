# Generated by Django 4.2.11 on 2024-06-19 08:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0030_product_quantity_alter_reservation_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='product_image_url',
            new_name='image_url',
        ),
        migrations.AlterField(
            model_name='reservation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 19, 16, 27, 13, 452827)),
        ),
    ]
