# Generated by Django 5.1.3 on 2024-12-03 17:44

import cuid2.generator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0003_remove_blogpage_tag_blogpage_category_blogpage_tags_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="waitinglistsignup",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
