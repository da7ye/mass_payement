# Generated by Django 5.1.7 on 2025-03-13 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0008_grouprecipient_failure_reason_grouprecipient_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipientgroup',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('partially_completed', 'Partially Completed')], default='pending', max_length=20),
        ),
    ]
