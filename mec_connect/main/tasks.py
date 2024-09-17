from __future__ import annotations

from typing import assert_never

from celery import shared_task
from celery.utils.log import get_task_logger

from .choices import ObjectType, WebhookEventStatus
from .clients import GristApiClient
from .models import GristConfig, WebhookEvent
from .services import (
    check_column_filters,
    fetch_projects_data,
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
            project_id = int(event.object_id)
        case ObjectType.SURVEY_ANSWER:
            project_id = int(event.object_data.get("project"))
        case _:
            assert_never(event.object_type)

    _update_project(project_id=project_id)

    event.status = WebhookEventStatus.PROCESSED
    event.save()


def _update_project(project_id: int) -> None:
    for config in GristConfig.objects.filter(enabled=True):
        for _, project_data in fetch_projects_data(config=config, project_ids=[project_id]):
            if not check_column_filters(filters=config.filters, obj=project_data):
                continue
            update_or_create_project_record(
                config=config, project_id=project_id, project_data=project_data
            )


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
        if not check_column_filters(filters=config.filters, obj=project_data):
            continue

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
        if not check_column_filters(filters=config.filters, obj=project_data):
            continue

        update_or_create_project_record(
            config=config, project_id=project_id, project_data=project_data
        )
