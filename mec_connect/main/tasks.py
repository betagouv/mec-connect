from __future__ import annotations

from celery import shared_task
from celery.utils.log import get_task_logger

from .choices import ObjectType, WebhookEventStatus
from .grist import GristApiClient, GristProjectRow
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
            pass

    event.status = WebhookEventStatus.PROCESSED
    event.save()


def process_project_event(event: WebhookEvent):
    for grist_config in GristConfig.objects.filter(enabled=True):
        client = GristApiClient.from_config(grist_config)

        resp = client.get_records(
            table_id=grist_config.table_id,
            filter={"object_id": [event.object_id]},
        )

        if len(records := resp["records"]):
            client.update_records(
                table_id=grist_config.table_id,
                records={
                    records[0]["id"]: GristProjectRow.from_payload_object(
                        obj=event.payload["object"]
                    ).to_dict(),
                },
            )
            continue

        client.create_records(
            table_id=grist_config.table_id,
            records=[
                {"object_id": event.object_id}
                | GristProjectRow.from_payload_object(obj=event.payload["object"]).to_dict(),
            ],
        )


def process_survey_answer_event(event: WebhookEvent):
    for grist_config in GristConfig.objects.filter(enabled=True):
        client = GristApiClient.from_config(grist_config)

        project_id = event.payload["object"]["project_id"]

        resp = client.get_records(
            table_id=grist_config.table_id,
            filter={"object_id": [project_id]},
        )
        records = resp["records"]

        if len(records) == 0:
            continue

        # TODO:update columns
