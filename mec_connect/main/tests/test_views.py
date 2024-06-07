from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime
from json import JSONEncoder
from typing import Any

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

default_payload = {
    "topic": "projects.Project/update",
    "object": {
        "id": 9,
        "created_on": "2023-11-03T08:47:56.292Z",
        "updated_on": "2024-02-22T13:38:55.248Z",
    },
    "object_type": "projects.Project",
    "webhook_uuid": "c209eaf7-8215-4346-9c75-82cf262dc5c3",
}

headers = {
    "Django-Webhook-UUID": "c209eaf7-8215-4346-9c75-82cf262dc5c3",
    "content-type": "application/json",
    # "django-webhook-signature-v1": "3bb57e3e6d0cdffe967d4557cb20dc7dd0e68a1091806d4a04afed87251c662a",  # noqa: E501
    # "django-webhook-request-timestamp": "1717761882",
}


def _webhook_headers(payload: dict[str, Any], headers: dict[str, str] = None):
    now = timezone.now()
    timestamp = int(datetime.timestamp(now))

    combined_payload = f"{timestamp}:{json.dumps(payload, cls=JSONEncoder)}"

    signature = hmac.new(
        key=settings.WEBHOOK_SECRET.encode(),
        msg=combined_payload.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return {
        "Django-Webhook-Request-Timestamp": str(timestamp),
        "Django-Webhook-Signature-v1": signature,
    } | (headers or {})


@pytest.mark.django_db
def test_webhook_ok(client):
    resp = client.post(
        reverse("api:webhook"),
        headers=_webhook_headers(default_payload, headers),
        data=default_payload,
    )
    assert resp.status_code == 200, resp.content


def test_invalid_signature(client, settings):
    settings.WEBHOOK_SECRET = "wrong-secret"
    resp = client.post(
        reverse("api:webhook"),
        headers=_webhook_headers(default_payload, headers),
        data=default_payload,
    )
    assert resp.status_code == 401, resp.content
