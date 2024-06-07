from __future__ import annotations

from django.core.management.base import BaseCommand, CommandParser
from main.grist import GristApiClient
from main.models import GristConfig
from main.recoco import RecocoApiClient


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

    def handle(self, *args, **options):
        try:
            config: GristConfig = GristConfig.objects.get(id=options["grist_config"])
        except GristConfig.DoesNotExist:
            self.stdout.write(self.style.ERROR("Config not found for the given UUID"))
            return

        if not config.enabled:
            self.stdout.write(self.style.ERROR("Config is not enabled"))
            return

        grist_client = GristApiClient.from_config(config)

        response = grist_client.get_tables()
        for table in response["tables"]:
            if table["id"] == config.table_id:
                self.stdout.write(
                    self.style.ERROR(f"Table {config.table_id} already exists, aborting...")
                )
                return

        self.stdout.write(f"Creating table {config.table_id} in Grist")
        grist_client.create_table(
            table_id=config.table_id,
            columns=config.formatted_table_columns,
        )

        recoco_client = RecocoApiClient()
        for project in recoco_client.get_projects():
            self.stdout.write(f"Creating project {project['name']} in Grist")

        # TODO: fill the table with records
        # grist_client.create_records(
        #     table_id=config.table_id,
        #     records=[...],
        # )
