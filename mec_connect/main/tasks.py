from __future__ import annotations

from typing import assert_never

from celery import shared_task
from celery.utils.log import get_task_logger

from .choices import ObjectType, WebhookEventStatus
from .clients import GristApiClient
from .models import GristConfig, WebhookEvent
from .services import (
    fetch_projects_data,
    process_project_event,
    process_survey_answer_event,
    update_or_create_project_record,
)

logger = get_task_logger(__name__)


@shared_task
def process_webhook_event(event_id: int):
    try:
        event = WebhookEvent.objects.get(id=event_id)
    except WebhookEvent.DoesNotExist:
        logger.error(f"WebhookEvent with id={event_id} does not exist")
        return

    match event.object_type:
        case ObjectType.PROJECT | ObjectType.TAGGEDITEM:
            process_project_event(event=event)
        case ObjectType.SURVEY_ANSWER:
            process_survey_answer_event(event=event)
        case _:
            assert_never(event.object_type)

    event.status = WebhookEventStatus.PROCESSED
    event.save()


@shared_task
def populate_grist_table(config_id: str):
    try:
        config = GristConfig.objects.get(id=config_id)
    except GristConfig.DoesNotExist:
        logger.error(f"GristConfig with id={config_id} does not exist")
        return

    grist_client = GristApiClient.from_config(config)

    grist_client.create_table(
        table_id=config.table_id,
        columns=config.table_columns,
    )

    batch_records = []
    batch_size = 100

    for project_id, project_data in fetch_projects_data(config=config):
        batch_records.append({"object_id": project_id} | project_data)

        if len(batch_records) > batch_size - 1:
            grist_client.create_records(table_id=config.table_id, records=batch_records)
            batch_records = []

    if len(batch_records) > 0:
        grist_client.create_records(table_id=config.table_id, records=batch_records)


@shared_task
def refresh_grist_table(config_id: str):
    try:
        config = GristConfig.objects.get(id=config_id)
    except GristConfig.DoesNotExist:
        logger.error(f"GristConfig with id={config_id} does not exist")
        return

    for project_id, project_data in fetch_projects_data(config=config):
        update_or_create_project_record(
            config=config, project_id=project_id, project_data=project_data
        )
