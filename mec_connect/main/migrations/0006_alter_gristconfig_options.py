# Generated by Django 5.0.6 on 2024-07-10 13:18
from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0005_remove_gristconfig_object_type"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="gristconfig",
            options={
                "ordering": ("-created",),
                "verbose_name": "Configuration Grist",
                "verbose_name_plural": "Configurations Grist",
            },
        ),
    ]