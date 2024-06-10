from __future__ import annotations

from django.core.management.base import BaseCommand, CommandParser
from main.grist import (
    GristApiClient,
    map_from_project_payload_object,
    map_from_survey_answer_payload_object,
)
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
                    self.style.ERROR(f"Table {config.table_id} already exists, aborting.")
                )
                return

        self.stdout.write(f"Creating table {config.table_id} in Grist")
        grist_client.create_table(
            table_id=config.table_id,
            columns=config.table_columns,
        )

        grist_table_headers = list(
            config.column_configs.values_list("grist_column__col_id", flat=True)
        )

        recoco_client = RecocoApiClient()

        for project in recoco_client.get_projects():
            self.stdout.write(f"Creating project {project['name']} in Grist")

            row_data = map_from_project_payload_object(
                obj=project, available_keys=grist_table_headers
            )

            sessions = recoco_client.get_survey_sessions(project_id=project["id"])
            if sessions["count"] > 0:
                answers = recoco_client.get_survey_session_answers(
                    session_id=sessions["results"][0]["id"]
                )
                for answer in answers["results"]:
                    row_data.update(
                        map_from_survey_answer_payload_object(
                            obj=answer, available_keys=grist_table_headers
                        )
                    )

            grist_client.create_records(
                table_id=config.table_id,
                records=[{"object_id": project["id"]} | row_data],
            )
