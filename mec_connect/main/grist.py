from __future__ import annotations

import abc
import json
from dataclasses import asdict, dataclass
from typing import Any, Self

from httpx import Client, Response

from .models import GristConfig


def raise_on_4xx_5xx(response: Response):
    response.raise_for_status()


class GristApiClient:
    api_key: str
    api_base_url: str
    doc_id: str

    def __init__(self, api_key: str, api_base_url: str, doc_id: str):
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.doc_id = doc_id

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

    def client_factory(self) -> Client:
        return Client(
            headers=self.headers,
            base_url=self.api_base_url,
            event_hooks={"response": [raise_on_4xx_5xx]},
        )

    def get_tables(self) -> dict[str, Any]:
        with self.client_factory() as client:
            resp = client.get(f"docs/{self.doc_id}/tables/")
            return resp.json()

    def create_table(self, table_id: str, columns: dict[str, Any]) -> dict[str, Any]:
        with self.client_factory() as client:
            resp = client.post(
                f"docs/{self.doc_id}/tables/",
                json={
                    "tables": [
                        {
                            "id": table_id,
                            "columns": [
                                {"id": k, "fields": {"label": v["label"]}}
                                for k, v in columns.items()
                            ],
                        }
                    ]
                },
            )
            return resp.json()

    def get_records(self, table_id: str, filter: dict[str, Any]) -> dict[str, Any]:
        with self.client_factory() as client:
            resp = client.get(
                f"docs/{self.doc_id}/tables/{table_id}/records/",
                params={"filter": json.dumps(filter)},
            )
            return resp.json()

    def create_records(self, table_id: str, records: list[dict[str, Any]]) -> dict[str, Any]:
        with self.client_factory() as client:
            resp = client.post(
                f"docs/{self.doc_id}/tables/{table_id}/records/",
                json={"records": [{"fields": r} for r in records]},
            )
            return resp.json()

    def update_records(self, table_id: str, records: dict[str, dict[str, Any]]) -> dict[str, Any]:
        with self.client_factory() as client:
            resp = client.patch(
                f"docs/{self.doc_id}/tables/{table_id}/records/",
                json={"records": [{"id": k, "fields": v} for k, v in records.items()]},
            )
            return resp.json()


class GristRow(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def from_payload_object(cls, obj: dict[str, Any]) -> Self:
        pass


@dataclass
class GristProjectRow(GristRow):
    name: str
    context: str | None = None
    additions: str | None = None
    topics: str | None = None
    details: str | None = None
    perimeter: str | None = None
    diagnostic_anct: str | None = None
    attachment: str | None = None
    diagnostic_is_shared: bool = False
    maturity: str | None = None
    ownership: str | None = None
    action: str | None = None
    partners: str | None = None
    budget: str | None = None
    forecast_financing_plan: str | None = None
    forecast_financing_plan_attachment: str | None = None
    final_financing_plan: str | None = None
    forecast_financing_plan_attachment: str | None = None
    calendar: str | None = None
    administrative_procedures: str | None = None
    dependencies: str | None = None
    evaluation_indicator: str | None = None
    ecological_transition_compass: str | None = None
    verdict: str | None = None
    grant_amount: float | None = None

    @classmethod
    def from_payload_object(cls, obj: dict[str, Any]) -> Self:
        return GristProjectRow(
            name=obj["name"],
            topics=", ".join(sorted([t["name"] for t in obj.get("topics", [])])),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
