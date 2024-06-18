from __future__ import annotations

from django.core.management.base import BaseCommand
from main.grist import default_columns_spec
from main.models import GristColumn


class Command(BaseCommand):
    def handle(self, *args, **options):
        for col_id, col_data in default_columns_spec.items():
            self.stdout.write(f"Creating column {col_id}")
            GristColumn.objects.update_or_create(
                col_id=col_id,
                defaults=col_data,
            )
