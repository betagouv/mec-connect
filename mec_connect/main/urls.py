from __future__ import annotations

from django.urls import path
from ninja import NinjaAPI

from .views import router

api = NinjaAPI(
    title="MEC Connect API",
    version="1.0.0",
    description="API for MEC Connect",
    openapi_url="/openapi.json",
    docs_url="/docs",
    urls_namespace="api",
)

api.add_router("", router)

urlpatterns = [
    path("api/", api.urls),
]
