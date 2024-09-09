from __future__ import annotations

from typing import Any, Self

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mec_connect.utils.json import PrettyJSONEncoder
from mec_connect.utils.models import BaseModel

from .choices import GristColumnType, ObjectType, WebhookEventStatus
from .managers import UserManager


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

    @property
    def object_data(self) -> dict[str, Any]:
        return self.payload.get("object", {})

    @classmethod
    def create_from_request(cls, request: WSGIRequest, **kwargs: dict[str, Any]) -> Self:
        return cls.objects.create(
            remote_ip=request.META.get("REMOTE_ADDR", "0.0.0.0"),
            headers=dict(request.headers),
            **kwargs,
        )


class GristConfig(BaseModel):
    name = models.CharField(max_length=255, blank=True, null=True)

    doc_id = models.CharField(max_length=32)
    table_id = models.CharField(max_length=32)
    enabled = models.BooleanField(default=True)

    api_base_url = models.CharField(max_length=128)
    api_key = models.CharField(max_length=64)

    class Meta:
        db_table = "gristconfig"
        ordering = ("-created",)
        verbose_name = "Configuration Grist"
        verbose_name_plural = "Configurations Grist"

    @property
    def table_columns(self) -> list[dict[str, Any]]:
        return [
            {
                "id": col_config.grist_column.col_id,
                "fields": {
                    "label": col_config.grist_column.label,
                    "type": GristColumnType(col_config.grist_column.type).label,
                },
            }
            for col_config in self.column_configs.select_related("grist_column")
        ]

    @property
    def table_headers(self) -> list[str]:
        return list(self.column_configs.values_list("grist_column__col_id", flat=True))


class GristColumn(BaseModel):
    col_id = models.CharField(max_length=64, unique=True)
    label = models.CharField(max_length=128)
    type = models.CharField(max_length=32, choices=GristColumnType.choices)

    class Meta:
        db_table = "gristcolumn"
        ordering = ("col_id",)
        verbose_name = "Grist column"
        verbose_name_plural = "Grist columns"

    def __str__(self) -> str:
        return self.label


class GritColumnConfig(BaseModel):
    grist_column = models.ForeignKey(
        GristColumn, on_delete=models.CASCADE, related_name="column_configs"
    )
    grist_config = models.ForeignKey(
        GristConfig, on_delete=models.CASCADE, related_name="column_configs"
    )
    position = models.IntegerField(default=0)

    class Meta:
        db_table = "gritcolumnconfig"
        ordering = (
            "position",
            "grist_column__col_id",
        )
        verbose_name = "Grit column config"
        verbose_name_plural = "Grit column configs"


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField(_("email address"), max_length=254, unique=True)
    first_name = models.CharField(_("first name"), max_length=254)
    last_name = models.CharField(_("last name"), max_length=254)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
