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
    TAGGEDITEM = "taggit.TaggedItem", "TaggedItem"


class GristColumnType(models.TextChoices):
    BOOL = "boolean", "Bool"
    CHOICE = "choice", "Choice"
    CHOICE_LIST = "choice_list", "ChoiceList"
    DATE = "date", "Date"
    INTEGER = "integer", "Int"
    NUMERIC = "numeric", "Numeric"
    TEXT = "text", "Text"


class FilterOperator(models.TextChoices):
    EQUAL = "eq", "Equal"
    I_EQUAL = "ieq", "Equal (case-insensitive)"
    NOT_EQUAL = "ne", "Not equal"
    I_NOT_EQUAL = "ine", "Not equal (case-insensitive)"
    CONTAINS = "contains", "Contains"
    I_CONTAINS = "icontains", "Contains (case-insensitive)"
