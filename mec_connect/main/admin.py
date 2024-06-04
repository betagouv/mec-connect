from __future__ import annotations

from django.contrib import admin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget

from .models import GristConfig, WebhookEvent


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "webhook_uuid",
        "topic",
        "object_id",
        "object_type",
        "status",
        "created",
    )

    list_filter = (
        "topic",
        "object_type",
        "status",
    )


@admin.register(GristConfig)
class GristConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "api_key",
        "api_base_url",
        "enabled",
        "object_type",
    )

    list_filter = (
        "enabled",
        "object_type",
    )

    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }
