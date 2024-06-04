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


@pytest.mark.django_db
def test_webhook(client):
    resp = client.post(
        reverse("api:webhook"),
        data=payload,
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
