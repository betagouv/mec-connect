from __future__ import annotations

from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from httpx import HTTPStatusError

from .choices import GristColumnType
from .models import (
    GristColumn,
    GristColumnFilter,
    GristConfig,
    GritColumnConfig,
    User,
    WebhookEvent,
)
from .services import (
    check_table_columns_consistency,
    grist_table_exists,
    update_or_create_columns_config,
)
from .tasks import populate_grist_table, refresh_grist_table


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


@admin.register(GristColumn)
class GristColumnAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "col_id",
        "label",
        "type",
    )
    search_fields = (
        "col_id",
        "label",
    )
    list_filter = ("type",)


class GristColumnInline(admin.TabularInline):
    model = GritColumnConfig
    extra = 0
    ordering = ("position", "grist_column__col_id")


class GristFilterInlineForm(forms.ModelForm):
    grist_column = forms.ModelChoiceField(
        queryset=GristColumn.objects.filter(
            type__in=(
                GristColumnType.BOOL,
                GristColumnType.TEXT,
                GristColumnType.NUMERIC,
                GristColumnType.INTEGER,
                GristColumnType.CHOICE,
                GristColumnType.CHOICE_LIST,
            )
        )
        .exclude(label__startswith="PJ")
        .order_by("label"),
    )


class GristFilterInline(admin.TabularInline):
    model = GristColumnFilter
    extra = 1
    ordering = ("grist_column__col_id",)
    form = GristFilterInlineForm


@admin.register(GristConfig)
class GristConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "api_base_url",
        "enabled",
    )

    list_filter = ("enabled",)

    inlines = (
        GristFilterInline,
        GristColumnInline,
    )

    actions = (
        "setup_grist_table",
        "reset_columns",
    )

    @admin.action(
        description="Créer ou mettre à jour la table Grist des configurations sélectionnées"
    )
    def setup_grist_table(self, request: HttpRequest, queryset: QuerySet[GristConfig]):
        for config in queryset:
            self._setup_grist_table_from_config(request, config)

    def _setup_grist_table_from_config(self, request: HttpRequest, config: GristConfig):
        if not config.enabled:
            self.message_user(
                request,
                f"Configuration {config}: inactive.",
                messages.ERROR,
            )
            return

        try:
            table_exists = grist_table_exists(config)
        except HTTPStatusError as err:
            if err.response.status_code == 404:
                self.message_user(
                    request,
                    f"Configuration {config}: le document {config.doc_id} n'existe pas.",
                    messages.ERROR,
                )
                return
            raise err

        if not table_exists:
            res = populate_grist_table.delay(config.id)
            self.message_user(
                request,
                f"Configuration {config}: une tâche de création a été lancée (task ID: {res.id}).",
                messages.SUCCESS,
            )
            return

        if not check_table_columns_consistency(config):
            self.message_user(
                request,
                f"Configuration {config}: les colonnes ne sont pas cohérentes. "
                f"Impossible de mettre à jour la table {config.table_id}.",
                messages.ERROR,
            )
            return

        res = refresh_grist_table.delay(config.id)
        self.message_user(
            request,
            f"Configuration {config}: une tâche de mise à jour a été lancée (task ID: {res.id}).",
            messages.SUCCESS,
        )

    @admin.action(
        description="Remettre les colonnes par défaut pour les configurations sélectionnées"
    )
    def reset_columns(self, request: HttpRequest, queryset: QuerySet[GristConfig]):
        for config in queryset:
            GritColumnConfig.objects.filter(grist_config=config).delete()
            update_or_create_columns_config(config=config)
            self.message_user(
                request,
                f"Configuration {config.id}: reset columns.",
                messages.SUCCESS,
            )


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
