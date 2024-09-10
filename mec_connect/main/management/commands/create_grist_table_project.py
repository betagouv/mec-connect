from __future__ import annotations

from django.core.management.base import BaseCommand, CommandParser
from main.clients.grist import grist_table_exists, table_columns_are_consistent
from main.models import GristConfig
from main.tasks import populate_grist_table, refresh_grist_table


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
        self.stdout.write(f" >> URL: {config.api_base_url}")
        self.stdout.write(f" >> doc ID: {config.doc_id}")
        self.stdout.write(f" >> table ID: {config.table_id}")

        task_func = None
        if grist_table_exists(config=config):
            if not table_columns_are_consistent(config=config):
                self.stdout.write(
                    self.style.ERROR("Columns in Grist table are not consistent with the config")
                )
                return
            task_func = refresh_grist_table
        else:
            self.stdout.write(f"Table {config.table_id} does not exist yet, calling populate")
            task_func = populate_grist_table

        self.stdout.write("\nStart processing ...")

        if options["async"]:
            task_func.delay(config.id)
            self.stdout.write(self.style.SUCCESS("Celery task triggered!"))
            return

        task_func.s(config.id)()
        self.stdout.write(self.style.SUCCESS("Done!"))
