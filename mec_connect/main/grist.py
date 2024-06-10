from __future__ import annotations

import json
from typing import Any, Self

from httpx import Client, Response

from .models import GristConfig


def raise_on_4xx_5xx(response: Response):
    response.raise_for_status()


class GristApiClient:
    api_key: str
    api_base_url: str
    doc_id: str
    client: Client

    def __init__(self, api_key: str, api_base_url: str, doc_id: str):
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.doc_id = doc_id
        self.client = Client(
            headers=self.headers,
            base_url=self.api_base_url,
            event_hooks={"response": [raise_on_4xx_5xx]},
        )

    @classmethod
    def from_config(cls, config: GristConfig) -> Self:
        return cls(
            api_key=config.api_key,
            api_base_url=config.api_base_url,
            doc_id=config.doc_id,
        )

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    def get_tables(self) -> dict[str, Any]:
        resp = self.client.get(f"docs/{self.doc_id}/tables/")
        return resp.json()

    def create_table(self, table_id: str, columns: dict[str, Any]) -> dict[str, Any]:
        resp = self.client.post(
            f"docs/{self.doc_id}/tables/",
            json={"tables": [{"id": table_id, "columns": columns}]},
        )
        return resp.json()

    def get_records(self, table_id: str, filter: dict[str, Any]) -> dict[str, Any]:
        resp = self.client.get(
            f"docs/{self.doc_id}/tables/{table_id}/records/",
            params={"filter": json.dumps(filter)},
        )
        return resp.json()

    def create_records(self, table_id: str, records: list[dict[str, Any]]) -> dict[str, Any]:
        resp = self.client.post(
            f"docs/{self.doc_id}/tables/{table_id}/records/",
            json={"records": [{"fields": r} for r in records]},
        )
        return resp.json()

    def update_records(self, table_id: str, records: dict[str, dict[str, Any]]) -> dict[str, Any]:
        resp = self.client.patch(
            f"docs/{self.doc_id}/tables/{table_id}/records/",
            json={"records": [{"id": k, "fields": v} for k, v in records.items()]},
        )
        return resp.json()


def map_from_project_payload_object(
    obj: dict[str, Any], available_keys: list[str] | None = None
) -> dict[str, Any]:
    data = {"name": obj["name"]}

    if available_keys is None:
        return data

    return {k: data[k] for k in available_keys if k in data}


def map_from_survey_answer_payload_object(
    obj: dict[str, Any], available_keys: list[str] | None = None
) -> dict[str, Any]:
    data = {}

    def _format_choices(_obj):
        return ",".join([c["text"] for c in _obj["choices"]])

    # TODO: need a question slug
    match obj["question"]["text_short"]:
        case "Thématique(s)":
            data["topics"] = _format_choices(obj)
        case "Description de l'action":
            data["action"] = obj["comment"]
        case "Partenaires":
            data["partners"] = obj["comment"]
        case "Calendrier":
            data["calendar"] = obj["comment"]
        case "Procédures administratives":
            data["administrative_procedures"] = obj["comment"]
        case "Autres programmes et contrats":
            data["dependencies"] = _format_choices(obj)
        case _:
            pass

    if available_keys is None:
        return data

    return {k: data[k] for k in available_keys if k in data}
