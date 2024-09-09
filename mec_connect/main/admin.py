from __future__ import annotations

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from main.grist import default_columns_spec, grist_table_exists
from main.tasks import populate_grist_table

from .models import GristColumn, GristConfig, GritColumnConfig, User, WebhookEvent


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


@admin.register(GristConfig)
class GristConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "api_base_url",
        "enabled",
    )

    list_filter = ("enabled",)

    inlines = (GristColumnInline,)

    actions = (
        "setup_grist_table",
        "reset_columns",
    )

    @admin.action(description="Créer la table Grist des configurations sélectionnées")
    def setup_grist_table(self, request: HttpRequest, queryset: QuerySet[GristConfig]):
        for config in queryset:
            self._setup_grist_table_from_config(request, config)

    def _setup_grist_table_from_config(self, request: HttpRequest, config: GristConfig):
        if not config.enabled:
            self.message_user(
                request,
                f"Configuration {config.id}: inactive.",
                messages.ERROR,
            )
            return

        if grist_table_exists(config):
            self.message_user(
                request,
                f"Configuration {config.id}: la table {config.table_id} existe déjà.",
                messages.ERROR,
            )
            return

        populate_grist_table.delay(config.id)
        self.message_user(
            request,
            f"Configuration {config.id}: une tâche a été lancée.",
            messages.SUCCESS,
        )

    @admin.action(
        description="Remettre les colonnes par défaut pour les configurations sélectionnées"
    )
    def reset_columns(self, request: HttpRequest, queryset: QuerySet[GristConfig]):
        for config in queryset:
            self._reset_columns_from_config(request, config)

    def _reset_columns_from_config(self, request: HttpRequest, config: GristConfig):
        GritColumnConfig.objects.filter(grist_config=config).delete()

        position = 0
        for col_id in default_columns_spec.keys():
            GritColumnConfig.objects.get_or_create(
                grist_column=GristColumn.objects.get(col_id=col_id),
                grist_config=config,
                defaults={"position": position},
            )
            position += 10

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
