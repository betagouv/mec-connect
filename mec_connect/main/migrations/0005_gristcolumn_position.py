# Generated by Django 5.0.6 on 2024-06-05 20:53
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_alter_gristconfig_columns_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="gristcolumn",
            name="position",
            field=models.IntegerField(default=0),
        ),
    ]