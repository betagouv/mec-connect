from __future__ import annotations

from django.core.management.base import BaseCommand
from main.services import update_or_create_columns


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_or_create_columns()
