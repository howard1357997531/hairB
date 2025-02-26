# Generated by Django 4.2.11 on 2024-06-24 07:04

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0038_order_total_price_alter_reservation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='pickup_method',
            field=models.CharField(choices=[('來店取', '來店取'), ('寄送指定地點', '寄送指定地點')], default='來店取', max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_state',
            field=models.CharField(choices=[('運送中', '運送中'), ('已送達', '已送達')], default='運送中', max_length=255),
        ),
        migrations.AlterField(
            model_name='item',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='line.order'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 24, 15, 4, 17, 843994)),
        ),
    ]
