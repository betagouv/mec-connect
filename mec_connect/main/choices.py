from __future__ import annotations

from django.db import models


class WebhookEventStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSED = "PROCESSED", "Processed"
    INVALID = "INVALID", "Invalid"
    FAILED = "FAILED", "Failed"


class ObjectType(models.TextChoices):
    PROJECT = "projects.Project", "Project"
    SURVEY_ANSWER = "survey.Answer", "Answer"


class GristColumnType(models.TextChoices):
    ATTACHMENTS = "attachments", "Attachments"
    BOOLEAN = "boolean", "Bool"
    DATE = "date", "Date"
    INTEGER = "integer", "Int"
    NUMERIC = "numeric", "Numeric"
    TEXT = "text", "Text"
