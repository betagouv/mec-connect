from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

admin.site.site_title = "MEC-Connect administration"
admin.site.site_header = f"MEC-Connect administration ({settings.ENVIRONMENT})"
admin.site.index_title = "MEC-Connect administration"


urlpatterns = [
    path("", include("main.urls")),
    path("admin/", admin.site.urls),
]
