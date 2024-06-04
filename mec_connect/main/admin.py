from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget

from .models import GristConfig, User, WebhookEvent


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


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
    )
    fieldsets = (
        (_("Security"), {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    search_fields = ("first_name", "last_name", "email")
    ordering = ("email",)
