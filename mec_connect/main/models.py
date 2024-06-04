from __future__ import annotations

from typing import Any, Self

from django.core.handlers.wsgi import WSGIRequest
from django.db import models

from mec_connect.utils.json import PrettyJSONEncoder
from mec_connect.utils.models import BaseModel

from .choices import ObjectType, WebhookEventStatus


class WebhookEvent(BaseModel):
    webhook_uuid = models.UUIDField()

    topic = models.CharField(
        max_length=32,
        help_text="Topic of the webhook event",
    )

    object_id = models.CharField(
        max_length=32,
        help_text="ID of the object that triggered the webhook event",
    )

    object_type = models.CharField(
        max_length=32,
        choices=ObjectType.choices,
        help_text="Type of the object that triggered the webhook event",
    )

    remote_ip = models.GenericIPAddressField(help_text="IP address of the request client.")
    headers = models.JSONField(default=dict)
    payload = models.JSONField(default=dict, encoder=PrettyJSONEncoder)

    status = models.CharField(
        max_length=32,
        choices=WebhookEventStatus.choices,
        default=WebhookEventStatus.PENDING,
        help_text="Whether or not the webhook event has been successfully processed",
    )

    exception = models.TextField(blank=True)
    traceback = models.TextField(
        blank=True,
        help_text="Traceback if an exception was thrown during processing",
    )

    class Meta:
        verbose_name = "Webhook Event"
        verbose_name_plural = "Webhook Events"
        db_table = "webhookevent"
        ordering = ("-created",)

    @classmethod
    def create_from_request(cls, request: WSGIRequest, **kwargs: dict[str, Any]) -> Self:
        return cls.objects.create(
            remote_ip=request.META.get("REMOTE_ADDR", "0.0.0.0"),
            headers=dict(request.headers),
            **kwargs,
        )


class GristConfig(BaseModel):
    doc_id = models.CharField(max_length=32)
    table_id = models.CharField(max_length=32)
    enabled = models.BooleanField(default=True)
    object_type = models.CharField(max_length=32, choices=ObjectType.choices)
    columns = models.JSONField(default=dict, encoder=PrettyJSONEncoder)

    api_base_url = models.CharField(max_length=128)
    api_key = models.CharField(max_length=64)

    class Meta:
        db_table = "gristconfig"
        ordering = ("-created",)
        verbose_name = "Grist configuration"
        verbose_name_plural = "Grist configurations"

    def clean(self) -> None:
        # if self.columns ...
        # raise ValidationError()
        pass
