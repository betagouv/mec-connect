from __future__ import annotations

import pytest
from django.urls import reverse

payload = {
    "topic": "projects.Project/update",
    "object": {
        "id": 9,
        "created_on": "2023-11-03T08:47:56.292Z",
        "updated_on": "2024-02-22T13:38:55.248Z",
    },
    "object_type": "projects.Project",
    "webhook_uuid": "dcb9e2c6-0781-41fd-bc78-80c5adafb2ea",
}

headers = {
    "django-webhook-uuid": "dcb9e2c6-0781-41fd-bc78-80c5adafb2ea",
    "Django-Webhook-Signature-v1": "e88c8ba1782769fe0a3060d55313f5b7900df007a9c6980a623a2d7deb40b696",  # noqa: E501
    "django-webhook-request-timestamp": "1717575565",
    "content-type": "application/json",
}


@pytest.mark.django_db
def test_webhook_ok(client):
    resp = client.post(reverse("api:webhook"), headers=headers, data=payload)
    assert resp.status_code == 200


def test_invalid_signature(client, settings):
    settings.WEBHOOK_SECRET = "wrong-secret"
    resp = client.post(reverse("api:webhook"), headers=headers, data=payload)
    assert resp.status_code == 401
