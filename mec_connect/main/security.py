from __future__ import annotations

import hmac
from hashlib import sha256
from typing import Any

from django.conf import settings
from django.http import HttpRequest
from ninja.errors import HttpError
from ninja.security.apikey import APIKeyHeader


class SecurityAuth(APIKeyHeader):
    param_name = "Django-Webhook-Signature-v1"

    def authenticate(self, request: HttpRequest, key: str | None) -> Any | None:
        req_timestamp = request.headers.get("Django-Webhook-Request-Timestamp")

        for signature in key.split(","):
            digest_payload = bytes(req_timestamp, "utf8") + b":" + request.body
            digest = hmac.new(
                key=settings.WEBHOOK_SECRET.encode(),
                msg=digest_payload,
                digestmod=sha256,
            )
            if not hmac.compare_digest(digest.hexdigest(), signature):
                raise HttpError(401, "Invalid signature")
