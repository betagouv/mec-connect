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

default_headers = {
    "Django-Webhook-UUID": "c209eaf7-8215-4346-9c75-82cf262dc5c3",
    "content-type": "application/json",
}


def _webhook_headers(payload: dict[str, Any], headers: dict[str, str] = None, secret: str = None):
    timestamp = int(datetime.timestamp(timezone.now()))
    combined_payload = f"{timestamp}:{json.dumps(payload, cls=JSONEncoder)}"
    secret = secret or settings.WEBHOOK_SECRET
    signature = hmac.new(
        key=secret.encode(),
        msg=combined_payload.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return {
        "Django-Webhook-UUID": "",
        "Django-Webhook-Request-Timestamp": str(timestamp),
        "Django-Webhook-Signature-v1": signature,
    } | (headers or {})


@pytest.mark.django_db
def test_webhook_ok(client):
    resp = client.post(
        reverse("api:webhook"),
        headers=_webhook_headers(default_payload, default_headers),
        data=default_payload,
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content


def test_invalid_signature(client):
    resp = client.post(
        reverse("api:webhook"),
        headers=_webhook_headers(default_payload, default_headers, secret="wrong-secret"),
        data=default_payload,
        content_type="application/json",
    )
    assert resp.status_code == 401, resp.content
