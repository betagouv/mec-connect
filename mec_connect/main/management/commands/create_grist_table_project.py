from __future__ import annotations

from django.core.management.base import BaseCommand, CommandParser
from main.grist import grist_table_exists
from main.models import GristConfig
from main.tasks import populate_grist_table


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--grist-config",
            required=True,
            type=str,
            help="UUID of the grist config we want to process",
            action="store",
            nargs="?",
        )

        parser.add_argument(
            "--async",
            action="store_true",
            help="Do it asynchronously (triggering a Celery task)",
        )

    def handle(self, *args, **options):
        try:
            config: GristConfig = GristConfig.objects.get(id=options["grist_config"])
        except GristConfig.DoesNotExist:
            self.stdout.write(self.style.ERROR("Config not found for the given UUID"))
            return

        if not config.enabled:
            self.stdout.write(self.style.ERROR("Config is not enabled"))
            return

        self.stdout.write(f"Processing Grist config {config.id}")
        if grist_table_exists(config):
            self.stdout.write(
                self.style.ERROR(f"Table {config.table_id} already exists, aborting.")
            )
            return

        self.stdout.write(f" >> URL: {config.api_base_url}")
        self.stdout.write(f" >> doc ID: {config.doc_id}")
        self.stdout.write(f" >> table ID: {config.table_id}")

        self.stdout.write("\nStart processing ...")

        if options["async"]:
            populate_grist_table.delay(config.id)
            self.stdout.write(self.style.SUCCESS("Celery task triggered!"))
            return

        populate_grist_table.s(config.id)()
        self.stdout.write(self.style.SUCCESS("Done!"))
