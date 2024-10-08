# Generated by Django 5.1.1 on 2024-09-20 08:06
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0009_gristcolumnfilter"),
    ]

    operations = [
        migrations.AddField(
            model_name="gristcolumnfilter",
            name="filter_operator",
            field=models.CharField(
                choices=[
                    ("eq", "Equal"),
                    ("ieq", "Equal (case-insensitive)"),
                    ("ne", "Not equal"),
                    ("ine", "Not equal (case-insensitive)"),
                    ("contains", "Contains"),
                    ("icontains", "Contains (case-insensitive)"),
                ],
                default="eq",
                max_length=32,
            ),
        ),
        migrations.AddIndex(
            model_name="gristcolumn",
            index=models.Index(fields=["type"], name="gristcolumn_type_fe5e45_idx"),
        ),
        migrations.AddIndex(
            model_name="gristconfig",
            index=models.Index(fields=["enabled"], name="gristconfig_enabled_c1b2e4_idx"),
        ),
    ]
