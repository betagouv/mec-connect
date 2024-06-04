from __future__ import annotations

from typing import assert_never

from celery import shared_task
from celery.utils.log import get_task_logger

from .choices import ObjectType, WebhookEventStatus
from .grist import GristApiClient, GristProjectRow
from .models import GristConfig, WebhookEvent

logger = get_task_logger(__name__)


def get_grist_row_class(object_type: str) -> type[GristProjectRow]:
    match object_type:
        case ObjectType.PROJECT:
            return GristProjectRow
        case _:
            assert_never(object_type, "Invalid object_type")


@shared_task
def process_webhook_event(event_id: int):
    try:
        event = WebhookEvent.objects.get(id=event_id)
    except WebhookEvent.DoesNotExist:
        logger.error(f"WebhookEvent with id={event_id} does not exist")
        return

    grist_row_class = get_grist_row_class(event.object_type)

    # TODO: move table_id to somewhere else, GristConfig?...
    table_id = "1"

    for grist_config in GristConfig.objects.filter(enabled=True, object_type=event.object_type):
        client = GristApiClient.from_config(grist_config)

        resp = client.get_records(
            table_id=table_id,
            filter={"object_id": [event.object_id]},
        )

        if len(records := resp["records"]):
            client.update_records(
                table_id="1",
                records={
                    records[0]["id"]: grist_row_class.from_payload_object(
                        obj=event.payload["object"]
                    ).to_dict(),
                },
            )
            continue

        client.create_records(
            table_id=table_id,
            records=[
                {"object_id": event.object_id}
                | grist_row_class.from_payload_object(obj=event.payload["object"]).to_dict(),
            ],
        )

    event.status = WebhookEventStatus.PROCESSED
    event.save()


@shared_task
def build_grist_table():
    pass
