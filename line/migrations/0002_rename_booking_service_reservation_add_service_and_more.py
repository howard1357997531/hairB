# Generated by Django 4.2.11 on 2024-05-14 07:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
        ('line', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reservation',
            old_name='booking_service',
            new_name='add_service',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='booking_datetime',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='is_canceled',
        ),
        migrations.AddField(
            model_name='reservation',
            name='date',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='service',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='staff_schedule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.staffschedule'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='time',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='designer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='designer', to='mainapp.lineuser'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='line_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='line_user', to='mainapp.lineuser'),
        ),
    ]
