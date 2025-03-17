# Generated by Django 5.1.7 on 2025-03-13 21:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_remove_templaterecipient_motive_recipientgroup_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipientgroup',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipient_groups', to='payments.user'),
        ),
    ]
