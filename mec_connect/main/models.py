from __future__ import annotations

from typing import Any, Self, assert_never

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mec_connect.utils.json import PrettyJSONEncoder
from mec_connect.utils.models import BaseModel

from .choices import FilterOperator, GristColumnType, ObjectType, WebhookEventStatus
from .managers import UserManager
from .utils import str2bool


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
        indexes = [
            models.Index(fields=["enabled"]),
        ]

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

    @property
    def filters(self, **kwargs: dict[str, Any]) -> list[GristColumnFilter]:
        return list(self.column_filters.filter(**kwargs))

    def __str__(self) -> str:
        return self.name or self.doc_id


class GristColumn(BaseModel):
    col_id = models.CharField(max_length=64, unique=True)
    label = models.CharField(max_length=128)
    type = models.CharField(max_length=32, choices=GristColumnType.choices)

    class Meta:
        db_table = "gristcolumn"
        ordering = ("col_id",)
        verbose_name = "Grist column"
        verbose_name_plural = "Grist columns"
        indexes = [
            models.Index(fields=["type"]),
        ]

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


class GristColumnFilter(BaseModel):
    grist_column = models.ForeignKey(
        GristColumn, on_delete=models.CASCADE, related_name="column_filters"
    )
    grist_config = models.ForeignKey(
        GristConfig, on_delete=models.CASCADE, related_name="column_filters"
    )

    filter_value = models.CharField(max_length=255)

    filter_operator = models.CharField(
        max_length=32, choices=FilterOperator.choices, default=FilterOperator.EQUAL
    )

    class Meta:
        db_table = "gristcolumnfilter"
        verbose_name = "Grist column filter"
        verbose_name_plural = "Grist column filters"

    def save(self, *args, **kwargs):
        try:
            self.cast_value(value=self.filter_value)
        except ValueError as err:
            raise ValueError(f"Invalid filter value: {self.filter_value}") from err
        return super().save(*args, **kwargs)

    def check_object(self, obj: dict[str, Any]) -> bool:
        if self.grist_column.col_id not in obj.keys():
            return False
        for k, v in obj.items():
            if k == self.grist_column.col_id:
                return self.check_value(v)
        return True

    def check_value(self, value: Any) -> bool:  # noqa: C901
        try:
            c_value = self.cast_value(value)
            c_filter_value = self.cast_value(self.filter_value)
        except ValueError:
            return False

        match self.filter_operator:
            case FilterOperator.EQUAL:
                return c_value == c_filter_value
            case FilterOperator.I_EQUAL:
                return c_value.lower() == c_filter_value.lower()
            case FilterOperator.NOT_EQUAL:
                return c_value != c_filter_value
            case FilterOperator.I_NOT_EQUAL:
                return c_value.lower() != c_filter_value.lower()
            case FilterOperator.CONTAINS:
                return c_filter_value in c_value
            case FilterOperator.I_CONTAINS:
                return c_filter_value.lower() in c_value.lower()
            case _:
                assert_never(self.filter_operator)

    def cast_value(self, value: str) -> Any:
        match self.grist_column.type:
            case GristColumnType.BOOL:
                return str2bool(value)
            case GristColumnType.INTEGER:
                return int(value)
            case GristColumnType.NUMERIC:
                return float(value)
            case GristColumnType.TEXT | GristColumnType.CHOICE | GristColumnType.CHOICE_LIST:
                return str(value)
            case _:
                raise ValueError(f"Unhandled column type: {self.grist_column.type}")


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
