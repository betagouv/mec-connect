from __future__ import annotations

from typing import assert_never

from celery import shared_task
from celery.utils.log import get_task_logger
from main.recoco import RecocoApiClient

from .choices import ObjectType, WebhookEventStatus
from .grist import (
    GristApiClient,
    map_from_project_payload_object,
    map_from_survey_answer_payload_object,
)
from .models import GristConfig, WebhookEvent

logger = get_task_logger(__name__)


@shared_task
def process_webhook_event(event_id: int):
    try:
        event = WebhookEvent.objects.get(id=event_id)
    except WebhookEvent.DoesNotExist:
        logger.error(f"WebhookEvent with id={event_id} does not exist")
        return

    match event.object_type:
        case ObjectType.PROJECT:
            process_project_event(event=event)
        case ObjectType.SURVEY_ANSWER:
            process_survey_answer_event(event=event)
        case _:
            assert_never(event.object_type)

    event.status = WebhookEventStatus.PROCESSED
    event.save()


def process_project_event(event: WebhookEvent):
    for grist_config in GristConfig.objects.filter(enabled=True):
        client = GristApiClient.from_config(grist_config)

        resp = client.get_records(
            table_id=grist_config.table_id,
            filter={"object_id": [str(event.object_id)]},
        )

        row_data = map_from_project_payload_object(
            obj=event.object_data,
            available_keys=grist_config.column_configs.values_list(
                "grist_column__col_id", flat=True
            ),
        )

        if len(records := resp["records"]):
            client.update_records(
                table_id=grist_config.table_id,
                records={
                    records[0]["id"]: row_data,
                },
            )
            continue

        client.create_records(
            table_id=grist_config.table_id,
            records=[{"object_id": event.object_id} | row_data],
        )


def process_survey_answer_event(event: WebhookEvent):
    for grist_config in GristConfig.objects.filter(enabled=True):
        client = GristApiClient.from_config(grist_config)

        project_id = str(event.object_data.get("project"))

        resp = client.get_records(
            table_id=grist_config.table_id,
            filter={"object_id": [project_id]},
        )

        if len(records := resp["records"]):
            row_data = map_from_survey_answer_payload_object(
                obj=event.object_data,
                available_keys=grist_config.column_configs.values_list(
                    "grist_column__col_id", flat=True
                ),
            )

            client.update_records(
                table_id=grist_config.table_id,
                records={
                    records[0]["id"]: row_data,
                },
            )


@shared_task
def populate_grist_table(config_id: str):
    config = GristConfig.objects.get(id=config_id)
    grist_table_columns = config.table_columns
    grist_table_headers = config.table_headers

    grist_client = GristApiClient.from_config(config)

    grist_client.create_table(
        table_id=config.table_id,
        columns=grist_table_columns,
    )

    recoco_client = RecocoApiClient()

    for project in recoco_client.get_projects():
        row_data = map_from_project_payload_object(obj=project, available_keys=grist_table_headers)

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
