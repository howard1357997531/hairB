# Generated by Django 4.2.11 on 2024-06-08 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0021_rename_punch_ou_timet_punchinorout_punch_out_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='punchinorout',
            name='is_take_leave',
            field=models.BooleanField(default=False),
        ),
    ]
