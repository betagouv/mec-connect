# Generated by Django 5.0.6 on 2024-06-10 16:29
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0003_gristcolumn_remove_gristconfig_columns_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gristcolumn",
            name="type",
            field=models.CharField(
                choices=[
                    ("boolean", "Bool"),
                    ("choice", "Choice"),
                    ("choice_list", "ChoiceList"),
                    ("date", "Date"),
                    ("integer", "Int"),
                    ("numeric", "Numeric"),
                    ("text", "Text"),
                ],
                max_length=32,
            ),
        ),
    ]