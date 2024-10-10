# Generated by Django 4.2.11 on 2024-05-23 03:30

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_staffschedule_is_full_alter_staffschedule_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffschedule',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 23, 11, 30, 28, 640752)),
        ),
        migrations.CreateModel(
            name='TakeLeave',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateTimeField()),
                ('start_hour', models.CharField(blank=True, max_length=255, null=True)),
                ('start_minute', models.CharField(blank=True, max_length=255, null=True)),
                ('end_hour', models.CharField(blank=True, max_length=255, null=True)),
                ('end_minute', models.CharField(blank=True, max_length=255, null=True)),
                ('category', models.CharField(blank=True, max_length=255, null=True)),
                ('remark', models.TextField(blank=True, null=True)),
                ('is_reviewed', models.BooleanField(default=False)),
                ('line_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lineUser', to='mainapp.lineuser')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
