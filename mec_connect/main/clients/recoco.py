from __future__ import annotations

from typing import Any

from django.conf import settings
from httpx import Auth, Client, Request, Response


class RecocoApiAuth(Auth):
    requires_response_body = True
    access_token: str = None
    refresh_token: str = None

    def auth_flow(self, request: Request):
        if self.access_token is None:
            token_response = yield self._build_token_request()
            self._update_tokens(token_response)
            request.headers["Authorization"] = f"Bearer {self.access_token}"
            yield request

        request.headers["Authorization"] = f"Bearer {self.access_token}"
        response = yield request

        if response.status_code == 401:
            refresh_response = yield self._build_refresh_request()
            self._update_tokens(refresh_response)
            request.headers["Authorization"] = f"Bearer {self.access_token}"
            yield request

    def _build_token_request(self):
        return Request(
            "POST",
            f"{settings.RECOCO_API_URL}/token/",
            data={
                "username": settings.RECOCO_API_USERNAME,
                "password": settings.RECOCO_API_PASSWORD,
            },
        )

    def _build_refresh_request(self):
        return Request(
            "POST",
            f"{settings.RECOCO_API_URL}/token/refresh/",
            data={
                "refresh": self.refresh_token,
            },
        )

    def _update_tokens(self, response: Response):
        payload = response.json()
        self.access_token = payload["access"]
        if "refresh" in payload:
            self.refresh_token = payload["refresh"]


def raise_on_4xx_5xx(response: Response):
    response.raise_for_status()


class RecocoApiClient:
    _client: Client

    def __init__(self, *args, **kwargs):
        self._client = Client(
            auth=RecocoApiAuth(),
            base_url=settings.RECOCO_API_URL,
            event_hooks={"response": [raise_on_4xx_5xx]},
            **kwargs,
        )

    def get_projects(self) -> dict[str, Any]:
        response = self._client.get("/projects/")
        return response.json()

    def get_project(self, project_id: int) -> dict[str, Any]:
        response = self._client.get(f"/projects/{project_id}/")
        return response.json()

    def get_survey_sessions(self, project_id: int) -> dict[str, Any]:
        response = self._client.get(f"/survey/sessions/?project_id={project_id}")
        return response.json()

    def get_survey_session_answers(self, session_id: int) -> dict[str, Any]:
        response = self._client.get(f"/survey/sessions/{session_id}/answers/")
        return response.json()
