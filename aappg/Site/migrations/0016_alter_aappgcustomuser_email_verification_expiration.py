# Generated by Django 5.0.7 on 2024-09-30 16:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Site', '0015_alter_aappgcustomuser_email_verification_expiration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aappgcustomuser',
            name='email_verification_expiration',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2024, 10, 1, 16, 51, 35, 106455, tzinfo=datetime.timezone.utc), null=True),
        ),
    ]
