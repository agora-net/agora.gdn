# Generated by Django 5.1.3 on 2024-11-20 10:56

from cuid2 import Cuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0004_waitinglistsignup_referral_code_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="waitinglistsignup",
            name="referral_code",
            field=models.CharField(
                default=Cuid(length=10).generate, max_length=10, unique=True
            ),
        ),
    ]
