# Generated by Django 4.2.11 on 2024-06-27 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0023_punchinorout_is_take_leave_approve'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminsetting',
            name='company_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='adminsetting',
            name='company_phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
