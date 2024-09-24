# Generated by Django 5.0.7 on 2024-09-23 18:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Site', '0012_alter_aappgcustomuser_email_verification_expiration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aappgcustomuser',
            name='email_verification_expiration',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2024, 9, 24, 18, 13, 22, 39496, tzinfo=datetime.timezone.utc), null=True),
        ),
        migrations.AlterField(
            model_name='aappgcustomuser',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
