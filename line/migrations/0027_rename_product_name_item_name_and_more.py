# Generated by Django 4.2.11 on 2024-06-17 02:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0026_alter_reservation_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='product_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='item',
            old_name='order_id',
            new_name='order',
        ),
        migrations.RenameField(
            model_name='item',
            old_name='product_price',
            new_name='price',
        ),
        migrations.AlterField(
            model_name='reservation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 17, 10, 59, 47, 228600)),
        ),
    ]
