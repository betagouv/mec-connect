from __future__ import annotations

from typing import Any

from ninja import Schema


class WebhookEventSchema(Schema):
    topic: str
    object: dict[str, Any]
    object_type: str
    webhook_uuid: str
