from __future__ import annotations

import uuid

from django.db import models
from model_utils.models import TimeStampedModel


class BaseModel(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    @property
    def uuid(self) -> uuid.UUID:
        return self.pk

    class Meta:
        abstract = True
