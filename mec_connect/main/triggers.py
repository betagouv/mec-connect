from __future__ import annotations

from .choices import WebhookEventStatus
from .models import WebhookEvent
from .tasks import process_webhook_event


def on_webhook_event_commit(event: WebhookEvent) -> None:
    if event.status != WebhookEventStatus.PENDING:
        return
    process_webhook_event.delay(event.id)
