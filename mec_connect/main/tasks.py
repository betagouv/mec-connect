from __future__ import annotations

from typing import assert_never

from celery import shared_task
from celery.utils.log import get_task_logger

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
            available_keys=grist_config.table_columns.values_list("col_id", flat=True),
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
                available_keys=grist_config.table_columns.values_list("col_id", flat=True),
            )

            client.update_records(
                table_id=grist_config.table_id,
                records={
                    records[0]["id"]: row_data,
                },
            )
