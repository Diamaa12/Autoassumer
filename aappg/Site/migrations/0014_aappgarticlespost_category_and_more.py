# Generated by Django 5.0.7 on 2024-09-29 00:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Site', '0013_alter_aappgcustomuser_email_verification_expiration_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='aappgarticlespost',
            name='category',
            field=models.CharField(choices=[('politique', 'Politique'), ('societe', 'Société'), ('economie', 'Économie'), ('guinee', 'Guinée'), ('diaspora', 'Diaspora'), ('communaute', 'Communauté'), ('histoire', 'Histoire')], default='politique', max_length=50),
        ),
        migrations.AlterField(
            model_name='aappgcustomuser',
            name='email_verification_expiration',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2024, 9, 30, 0, 16, 56, 879136, tzinfo=datetime.timezone.utc), null=True),
        ),
    ]
