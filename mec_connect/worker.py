from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mec_connect.settings.default")

app = Celery("mec-connect")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
